# coding=utf-8


from flask import current_app
from werkzeug.utils import safe_join
from werkzeug.exceptions import NotFound
from pygit2 import GitError, Repository
from pygit2.enums import ObjectType

def get_repo(repo_key):
    repo_dirs = [repo_key, f"{repo_key}.git"]
    for repo_dir in repo_dirs:
        repo_path = safe_join(current_app.config['RESTFULGIT_REPO_BASE_PATH'], repo_dir)
        try:
            return Repository(repo_path)
        except GitError:
            continue
    raise NotFound("repository not found")


def get_commit(repo, sha):
    try:
        commit = repo[str(sha)]
    except KeyError:
        raise NotFound("commit not found")
    if commit.type != ObjectType.COMMIT:
        raise NotFound("object not a commit")
    return commit


def get_tree(repo, sha):
    try:
        obj = repo[str(sha)]
    except KeyError:
        raise NotFound("tree not found")
    if obj.type == ObjectType.TREE:
        return obj
    elif obj.type == ObjectType.COMMIT:
        return obj.tree
    elif obj.type == ObjectType.TAG:
        obj = repo[obj.target]
        if obj.type == ObjectType.TAG:
            return get_tree(repo, obj.target)
        else:
            return obj.tree
    else:
        raise NotFound("object not a tree, a commit or a tag")


def get_blob(repo, sha):
    try:
        blob = repo[str(sha)]
    except KeyError:
        raise NotFound("blob not found")
    if blob.type != ObjectType.BLOB:
        raise NotFound("sha not a blob")
    return blob


def get_tag(repo, sha):
    try:
        tag = repo[str(sha)]
    except KeyError:
        raise NotFound("tag not found")
    if tag.type != ObjectType.TAG:
        raise NotFound("object not a tag")
    return tag


def lookup_ref(repo, ref_name):
    try:
        return repo.lookup_reference(ref_name)
    except (ValueError, KeyError):
        if "/" in ref_name and not ref_name.startswith("refs/"):
            ref_name = "refs/" + ref_name
        else:
            ref_name = "refs/heads/" + ref_name

        try:
            return repo.lookup_reference(ref_name)
        except (ValueError, KeyError):
            return None
