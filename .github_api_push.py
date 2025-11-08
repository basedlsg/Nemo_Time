import base64
import json
import os
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from typing import List, Dict

API_BASE = "https://api.github.com"


def run(cmd: List[str]) -> str:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return res.stdout.strip()


def get_remote_info() -> Dict[str, str]:
    url = run(["git", "remote", "get-url", "origin"])  # may include token
    # Expect formats:
    # https://TOKEN@github.com/owner/repo.git
    if not url.startswith("https://"):
        print("Only https remotes are supported by this script.", file=sys.stderr)
        sys.exit(2)
    try:
        auth_and_host, path = url[len("https://"):].split("@github.com/", 1)
    except ValueError:
        print("Unexpected remote URL format.", file=sys.stderr)
        sys.exit(2)
    token = auth_and_host  # don't print
    if path.endswith(".git"):
        path = path[:-4]
    try:
        owner, repo = path.split("/", 1)
    except ValueError:
        print("Could not parse owner/repo from remote URL.", file=sys.stderr)
        sys.exit(2)
    return {"token": token, "owner": owner, "repo": repo}


def api_request(token: str, method: str, url: str, payload: Dict | None = None, extra_headers: Dict[str, str] | None = None) -> Dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read()
                if not body:
                    return {}
                return json.loads(body.decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code in (429, 502, 503, 504):
                pass
            elif isinstance(e, urllib.error.URLError):
                pass
            else:
                raise
        # backoff
        import time
        time.sleep(2 ** attempt)
    # final try (will raise if fails)
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read()
        if not body:
            return {}
        return json.loads(body.decode("utf-8"))


def list_tracked_files() -> List[str]:
    res = subprocess.run(["git", "ls-files", "-z"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    raw = res.stdout
    parts = raw.split(b"\x00")
    files: List[str] = []
    for b in parts:
        if not b:
            continue
        try:
            s = b.decode("utf-8", errors="surrogateescape")
        except Exception:
            s = b.decode("latin1", errors="replace")
        files.append(s)
    return files


def is_executable(path: str) -> bool:
    try:
        st = os.stat(path)
        return bool(st.st_mode & stat.S_IXUSR)
    except FileNotFoundError:
        return False


def bootstrap_repo_with_readme(token: str, owner: str, repo: str, branch: str = "main") -> None:
    content = base64.b64encode(b"Bootstrap commit").decode("ascii")
    # Use Contents API to create a file and implicitly create the branch
    api_request(
        token,
        "PUT",
        f"{API_BASE}/repos/{owner}/{repo}/contents/README.md",
        {
            "message": "Bootstrap repo",
            "content": content,
            "branch": branch,
        },
    )


def create_blobs(token: str, owner: str, repo: str, files: List[str]) -> Dict[str, str]:
    file_to_blob: Dict[str, str] = {}
    for p in files:
        with open(p, "rb") as f:
            content = f.read()
        b64 = base64.b64encode(content).decode("ascii")
        resp = api_request(
            token,
            "POST",
            f"{API_BASE}/repos/{owner}/{repo}/git/blobs",
            {"content": b64, "encoding": "base64"},
        )
        file_to_blob[p] = resp["sha"]
    return file_to_blob


def create_tree(token: str, owner: str, repo: str, file_to_blob: Dict[str, str]) -> str:
    tree = []
    for path, sha in file_to_blob.items():
        mode = "100755" if is_executable(path) else "100644"
        tree.append({"path": path, "mode": mode, "type": "blob", "sha": sha})
    resp = api_request(
        token,
        "POST",
        f"{API_BASE}/repos/{owner}/{repo}/git/trees",
        {"tree": tree},
    )
    return resp["sha"]


def create_commit(token: str, owner: str, repo: str, tree_sha: str, message: str, parent_sha: str | None = None) -> str:
    payload: Dict[str, object] = {"message": message, "tree": tree_sha}
    if parent_sha:
        payload["parents"] = [parent_sha]
    resp = api_request(
        token,
        "POST",
        f"{API_BASE}/repos/{owner}/{repo}/git/commits",
        payload,
    )
    return resp["sha"]


def get_branch_sha(token: str, owner: str, repo: str, branch: str) -> str | None:
    try:
        resp = api_request(token, "GET", f"{API_BASE}/repos/{owner}/{repo}/git/ref/heads/{branch}")
        return resp.get("object", {}).get("sha")
    except urllib.error.HTTPError as e:
        if e.code in (404, 409):
            return None
        raise


def ensure_ref(token: str, owner: str, repo: str, ref: str, sha: str) -> None:
    # Try to create the ref; if it exists, update it with force
    try:
        api_request(
            token,
            "POST",
            f"{API_BASE}/repos/{owner}/{repo}/git/refs",
            {"ref": f"refs/heads/{ref}", "sha": sha},
        )
    except urllib.error.HTTPError as e:
        if e.code == 422:
            api_request(
                token,
                "PATCH",
                f"{API_BASE}/repos/{owner}/{repo}/git/refs/heads/{ref}",
                {"sha": sha, "force": True},
            )
        else:
            raise


def main() -> None:
    info = get_remote_info()
    token = info["token"]
    owner = info["owner"]
    repo = info["repo"]

    files = list_tracked_files()
    if not files:
        print("No tracked files to push.")
        return

    print(f"Preparing to push {len(files)} files to {owner}/{repo} via GitHub API...")

    # Ensure repo has an initial branch; bootstrap if necessary
    branch = "main"
    head_sha = get_branch_sha(token, owner, repo, branch)
    if head_sha is None:
        # Create initial file to materialize the branch
        bootstrap_repo_with_readme(token, owner, repo, branch)

    # Push in batches to reduce API pressure
    BATCH = 200
    total = len(files)
    start = 0
    batch_index = 1
    while start < total:
        chunk = files[start:start+BATCH]
        file_to_blob = create_blobs(token, owner, repo, chunk)
        tree_sha = create_tree(token, owner, repo, file_to_blob)
        parent = get_branch_sha(token, owner, repo, branch)
        commit_sha = create_commit(token, owner, repo, tree_sha, f"Automated sync via API (batch {batch_index})", parent_sha=parent)
        ensure_ref(token, owner, repo, branch, commit_sha)
        print(f"Pushed batch {batch_index}: {len(chunk)} files")
        start += BATCH
        batch_index += 1
    print("Push completed via GitHub API.")


if __name__ == "__main__":
    main()
