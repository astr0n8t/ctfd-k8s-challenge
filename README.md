# ctfd-k8s-challenge

A Kubernetes challenge type plugin for CTFd

This plugin provides three new challenge types for CTFd: k8s-tcp, k8s-web, and k8s-random-port.

Each type allows for an on-demand, per user (or team) challenge instances that are deployed in Kubernetes and available externally immediately (*usually*).

## Motivation

This project was born because there doesn't seem to be something that does this aside from the paid for platform from CTFd.  While that's great for people that want a managed solution, sometimes it's also nice to be able to spin up your own self-hosted instance that has the same functionality.

This plugin aims to make it easy to turn Kubernetes into a CTF platform through CTFd.

## Requirements

This plugin is highly extensible by design.

The bare minimum requirements to get started are:

- A Deployed Kubernetes Cluster
- A CTFd instance deployed
    - Note: this doesn't need to be in the k8s cluster necessarily.

Some other requirements that are required if you use the templates I've built:

- Istio deployed in your Kubernetes cluster
- Wildcard DNS records pointing to your Istio ingress gateway
- cert-manager deployed in your Kubernetes cluster

### Custom Templates

You can replace any of the templates in the templates folder with your own.  Don't like how I designed the aspects or want to bring your own registry?  Just re-write the YAML to your own.  The plugin reads in the YAML and deploys them just like you would with kubectl.  That's why technically you don't need Istio or cert-manager (although I recommend it to make things easier).

## Challenge Types

### k8s-tcp

This challenge type is for typical connections which would happen over something like netcat or a raw TCP socket.  These challenges will be secured by TLS and routed by Istio using SNI.  These should work for most binexp, RE, or crypto challenges.  You will need to provide players with a tool like [snicat](https://github.com/CTFd/snicat) to access these; some tools like `pwntools` also support this; you can also do it with openssl's s_client.

### k8s-web

This challenge type is for HTTP services.  These need to be different from the normal TLS/TCP challenges due to the way the routing needs to be handled by Istio when using wildcard certificates.  This is actually due to a [long standing bug](https://github.com/istio/istio/issues/13589) in Istio where it does not properly tell browsers that they are talking to the wrong host. If this is ever resolved, web and tcp challenges can be created in exactly the same way without any issues.

### k8s-random-port

This challenge type is still for TCP services.  These are for services that cannot be served behind TLS/SNI properly.  The workflow is that CTFd will generate a unique port between 40000 and 50000 for each instance in combination with a unique domain name, except that the domain name will not matter in this case since we cannot use SNI.

If UDP/\<insert obscure proto here\> is needed, the idea is that someone can simply do an OpenVPN port or SSH on the random port and then have players pivot through those.

## Installation

See [installation](docs/installation.md)

## Configuration 

See [configuration](docs/configuration.md)

## Templates 

This plugin deploys templated YAML files for various things such as challenge instances.  You can customize these as you need to and probably should as the defaults have container limits set on challenge instances that may not work with your challenges.  I would also recommend looking into also using something like [Google's nsjail](https://github.com/google/nsjail) for security as well as following Google's recommended best practices for their [kctf project](https://google.github.io/kctf/).

See [templates](docs/templates.md)

## Architecture Overview

See [architecture](docs/architecture.md)

## Issues?

Open an issue, I don't actively work on this project (aside from writing this documentation 2 years after the fact), but I'm happy to try to assist if you hit an issue.

