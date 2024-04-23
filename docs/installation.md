# Installing

The basic way to install this plugin is the same as any other CTFd plugin.

I recommend baking it into your CTFd container (assuming you're using containers):

## Containerized

In your `Dockerfile`
```
FROM ctfd/ctfd
USER 0
COPY ./CTFd/ /opt/CTFd/CTFd

# hadolint ignore=SC2086
RUN for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install -r $d/requirements.txt --no-cache-dir; \
        fi; \
    done;
USER 1001
```

And then within that `CTFd` folder make a plugins folder, and then clone this repository into it:
```
mkdir -p CTFd/plugins && cd CTFd/plugins
git clone https://github.com/astr0n8t/ctfd-k8s-challenge.git
```

And then build your container.

## Non-containerized

Should be fairly similar (I've never done it this way though):

1. Clone this repository to `/opt/CTFd/CTFd/plugins`
2. Run `pip install -r requirements.txt` inside the repository
3. Restart CTFd

## Post-Install

Now you should be ready to start [configuring](configuration.md).

