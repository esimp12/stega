import tomllib
from pathlib import Path

from invoke import task

_ROOT_CONFIG = "uv.lock"

# TODO: Add a way to build only individual packages (for python)
# TODO: Add a way to build only individual packages (for docker)
# TODO: Add a way to test all packages
# TODO: Add a way to migrate individual packages
# TODO: Add a way to migrate all packages
# TODO: Add a way to clean individual packages
# TODO: Add a way to clean all packages
# TODO: Add a way to lint individual packages
# TODO: Add a way to lint all packages
# TODO: Add a way to format individual packages
# TODO: Add a way to format all packages


@task
def build_services(c):
    """Build all service packages and their dependencies."""
    # Discover all member packages and their dependencies
    print("Discovering member packages and their dependencies...")
    deps = _resolve_member_deps(_ROOT_CONFIG)
    deps = _resolve_service_deps(deps)
    print(f"Found {len(deps)} service packages with dependencies.")
    for name, info in deps.items():
        print(f"Package: {name}, Path: {info['path']}, Dependencies: {info['dependencies']}")

    # Build each service package and its dependencies
    print("Building service packages and their dependencies...")
    for name, info in deps.items():
        dist_path = Path(info["path"]) / "dist"
        dist_path.mkdir(parents=True, exist_ok=True)

        # Create the third party dependencies file
        print(f"Exporting requirements for {name} to {dist_path / 'requirements.txt'}...")
        c.run(
            f"uv export --quiet --format requirements.txt --frozen --package {name} "
            f"--no-editable --no-emit-workspace --no-dev -o {dist_path / 'requirements.txt'}",
        )
        print("Exported requirements.")

        # Build the package
        print(f"Building package {name} at {dist_path}...")
        c.run(f"uv build --quiet --package {name} -o {dist_path}")
        print(f"Built package {name}.")

        # Build each dependency
        print(f"Building dependencies for {name} at {dist_path}...")
        for dep in info["dependencies"]:
            print(f"Building dependency {dep} at {dist_path}...")
            c.run(f"uv build --quiet --package {dep} -o {dist_path}")
            print(f"Built dependency {dep}.")
        print("All dependencies built.")
    print("All service packages built.")


@task(pre=[build_services])
def build_images(c):
    """Build Docker images for all service packages."""
    print("Building Docker images for all service packages...")
    c.run("docker compose build")
    print("Docker images built successfully.")


@task(pre=[build_images])
def build(c):
    """Build all service packages and their dependencies."""


@task(pre=[build_services])
def serve(c, package, env_file=".env.dev"):
    """Serve a single service locally in development mode."""
    services = _get_service_names(_ROOT_CONFIG)
    if package not in services:
        raise ValueError(f"Package '{package}' is not a known service package.")
    if not Path(env_file).exists():
        raise FileNotFoundError(f"Environment file '{env_file}' does not exist.")

    print(f"Serving package {package} locally...")
    c.run(f"uv run --env-file {env_file} --package {package} serve")


@task(pre=[build_services])
def test(c, package):
    """Run tests for a single service package."""
    deps = _resolve_member_deps(_ROOT_CONFIG)
    deps = _resolve_service_deps(deps)
    if package not in deps.keys():
        raise ValueError(f"Package '{package}' is not a known service package.")

    print(f"Running tests for package {package}...")
    c.run(f"uv run --package {package} --directory {deps[package]['path']} pytest")


@task(pre=[build])
def deploy(c, env_file=".env.prod"):
    """Deploy the application to a production environment."""
    if not Path(env_file).exists():
        raise FileNotFoundError(f"Environment file '{env_file}' does not exist.")
    print("Deploying the application...")
    c.run(f"docker compose --env-file {env_file} up -d ")
    print("Deployment completed.")


def _get_service_names(manifest_path):
    manifest = _load_manifest(manifest_path)
    members = manifest["manifest"]["members"]
    member_pkgs = [pkg for pkg in manifest["package"] if pkg["name"] in members]
    member_pkgs = [pkg for pkg in member_pkgs if not _is_virtual_package(pkg)]
    service_names = []
    for pkg in member_pkgs:
        pkg_config_path = Path(_get_pkg_source(pkg)) / "pyproject.toml"
        pkg_manifest = _load_manifest(pkg_config_path)
        if _is_service_package(pkg_manifest):
            service_names.append(pkg["name"])
    return service_names


def _resolve_service_deps(member_deps):
    service_deps = {
        name: info
        for name, info in member_deps.items()
        if _is_service_package(_load_manifest(Path(info["path"]) / "pyproject.toml"))
    }
    return service_deps


def _is_service_package(pkg):
    if "tool" not in pkg:
        return False
    if "stega" not in pkg["tool"]:
        return False
    return pkg["tool"]["stega"].get("service", False)


def _resolve_member_deps(manifest_path):
    manifest = _load_manifest(manifest_path)

    # Find member packages in the manifest
    members = manifest["manifest"]["members"]
    member_pkgs = [pkg for pkg in manifest["package"] if pkg["name"] in members]

    # Filter out any virtual packages
    member_pkgs = [pkg for pkg in member_pkgs if not _is_virtual_package(pkg)]

    # Construct dependency map for each member package
    member_deps = {
        pkg["name"]: {"path": _get_pkg_source(pkg), "dependencies": _get_pkg_deps(pkg, members)} for pkg in member_pkgs
    }
    return member_deps


def _get_pkg_source(pkg):
    return str(Path(pkg["source"]["editable"]).absolute())


def _get_pkg_deps(pkg, members):
    if "dependencies" not in pkg:
        return []
    return [dep["name"] for dep in pkg["dependencies"] if dep["name"] in members]


def _is_virtual_package(pkg):
    if "source" not in pkg:
        return False
    return "virtual" in pkg["source"]


def _load_manifest(manifest_path):
    with open(manifest_path, "rb") as fd:
        return tomllib.load(fd)
