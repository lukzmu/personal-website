Title: Keeping your pi agent in a box.
Date: 2026-11-06 10:00
Model: gemma-4-26B-A4B-it-oQ8e-mtp
Tool: pi

For some time now, I've been looking into running my agents locally to preserve the last bits of my privacy in this tech-driven world. Every request I send to `claude` makes me feel like I'm selling my soul to Big Tech companies, and that's not a good thing. So, like in other things, I started exploring open-source projects that would allow me to achieve this goal.

You can check [orion](https://github.com/lukzmu/orion) for the code and configurations I use for my pi agents.

## The Problem

I decided to go with the [pi coding agent](https://pi.dev). What I love about it is that it gives you full control over the configuration - it provides a base without forcing unnecessary dependencies on you. This flexibility fits my worldview perfectly...

...but it comes at a price. When I was testing some models, they were extremely aggressive in their exploration *(Qwen, I'm looking at you)*. They were touching files on my disk that I never intended for them to see. Obviously, I needed to build a sandbox to ensure they stayed exactly where they belonged.

## Containers, containers everywhere

The [pi security documentation](https://pi.dev/docs/latest/security) treats running the harness securely as a vital task and points to containers and isolated environments as a primary solution. Since I'm constantly hosting containers on `podman` on my system, it made sense to reuse my existing workflow for this *"project"*.

::: chat Łukasz
Think of it as a Schrödinger's Agent: until you run the container, we don't know if the model will be a helpful assistant or a chaotic entity trying to explore your entire home directory.
:::

Let's start with how a `Dockerfile` could look:

```dockerfile
FROM node:26.12-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates curl git ripgrep \
    && rm -rf /var/lib/apt/lists/*

ARG PI_VERSION=latest
RUN npm install -g --ignore-scripts @earendil-works/pi-coding-agent@${PI_VERSION}

ENTRYPOINT ["pi"]
```

As you can see, it's very minimal. I installed only the essentials for `pi` to run and included the ability to pin the version (I used `latest` for testing). Let's build the image and give it a name so it's easier to reuse:

```bash
podman build -t orion -f Dockerfile .
```

Now for the important part: running it. I mount the current project at the *same path* inside the container and use it as the working directory, so paths the agent prints match the ones on my host:

```bash
podman run --rm -it \
    -v "$PWD:$PWD" \
    -w "$PWD" \
    -v "$HOME/.pi/agent:/root/.pi/agent" \
    "orion"
```

The agent can now freely modify files in that one directory and nothing else on your disk. The only other mount is `~/.pi/agent`, which keeps `pi`'s configuration and sessions between runs. Keep in mind that this directory is writable from inside the container, so treat it as trusted: anything the agent changes there will affect your future sessions too.

You probably don't want to type this command every time you want to run `pi` in a container. You can either create an `alias` or use a [start script](https://github.com/lukzmu/orion/blob/main/run.sh) like I did.

## This is great, but...

Files aren't everything. You probably want to reuse your project configurations (Python, Rust) or your Git identity... and suddenly, those are unavailable inside the container the agent is working on.

### So how do we commit files?

For starters, I added the following to my `Dockerfile` so the system trusts every repository inside the container:

```dockerfile
RUN git config --system safe.directory '*'
```

When running the image, I can pass my Git identity as environment variables:

```bash
podman run --rm -it \
    -e GIT_AUTHOR_NAME="$GIT_NAME" \
    -e GIT_AUTHOR_EMAIL="$GIT_EMAIL" \
    -e GIT_COMMITTER_NAME="$GIT_NAME" \
    -e GIT_COMMITTER_EMAIL="$GIT_EMAIL" \
    "orion"
```

With this, the agent can commit on your behalf without touching your host's global config. Note that this is only your name and email: the container has no SSH keys or tokens, so the agent can commit but can't push. I consider that a feature.

### Tooling? I want to work on my project.

This is a tricky one. Some guides suggest adding every possible tool to your `Dockerfile` *(or create multiple new ones)*. I avoided this because I don't want to bloat a minimal image with a massive layer of dependencies. 

Instead, I use [mise-en-place](https://mise.jdx.dev/). It allows you to configure all the tools, environments, and tasks required for your project on the fly. It's the perfect companion for containerized agents. I even added `mise` to my `Dockerfile` so `pi` can pick it up and run commands in the correct environment:

```dockerfile
RUN curl -fsSL https://mise.run | sh
ENV PATH="/root/.local/bin:/root/.local/share/mise/shims:${PATH}"
```

Since the container is started with `--rm`, every run would download the toolchains from scratch. Mounting a cache volume fixes that:

```bash
podman run --rm -it \
    -v orion-mise:/root/.local/share/mise \
    "orion"
```

### How does the agent reach my local model?

The model server runs on the host, not inside the container, so `localhost` won't work from within it. Podman exposes the host as `host.containers.internal`, so point your provider's base URL at something like `http://host.containers.internal:8080/v1` (use the port of your inference server).

### And what, if I just want to chat?

Sometimes I want to use `pi` just to have a conversation, without working on a specific project. I decided to use the container's own `/tmp` directory as my workspace. Nothing from the host is mounted there, so it contains nothing of value. I updated my `run.sh` to support a `--chat` flag:

```bash
CHAT_MODE=false
ARGS=()

for arg in "$@"; do
    if [ "$arg" = "--chat" ]; then
        CHAT_MODE=true
    else
        ARGS+=("$arg")
    fi
done

# ... (logic to build PODMAN_ARGS)

if [ "$CHAT_MODE" = true ]; then
    PODMAN_ARGS+=(-w /tmp)
else
    PODMAN_ARGS+=(-v "$PWD:$PWD" -w "$PWD")
fi

podman run "${PODMAN_ARGS[@]}" "$IMAGE" "${ARGS[@]}"
```

This way, if the model tries to go rogue and look for sensitive data, it'll just find an empty `/tmp` folder. What a pity.

::: chat Łukasz
I'm sorry, Pi, I'm afraid I can't let you access that directory.
:::

## What this doesn't protect you from

A container is a fence, not a vault, so it's worth knowing where the fence ends:

- **Network access.** The container can still reach the network. Running models locally is what keeps your prompts private, while the container only keeps the agent out of your files. These are two separate concerns.
- **Whatever you mount.** The agent has full access to your project directory and to `~/.pi/agent`. If you run `run.sh` from `~`, you've just mounted your entire home directory. Obviously, don't do that.
- **The shared kernel.** Containers are not virtual machines. For a hostile model, you'd want a VM. For an over-curious one, a container is plenty.

## Summary

By containerizing the `pi` agent, I've achieved a balance between powerful AI assistance and local security. Using `podman` allows me to isolate the agent's file system access, while tools like `mise-en-place` and environment variable injection ensure that I don't lose the developer experience. It's a simple setup, and while it's no perfect sandbox, it gives me the peace of mind that my files stay mine, even when an aggressive model is trying to learn everything about my life.
