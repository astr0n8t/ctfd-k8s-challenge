# ctfd-k8s-challenge
A Kubernetes challenge type plugin for CTFd

There will be three different challenges types for Kubernetes depending on the different services each provides.  Certain challenges have different use cases.

## k8s-tcp

This challenge type is for typical connections which would happen over something like netcat or a raw TCP socket.  These challenges will be secured by TLS and routed by Istio using SNI.  These should work for most binexp, RE, or crypto challenges.

## k8s-web

This challenge type is for HTTP services.  These need to be different from the normal TLS/TCP challenges due to the way the routing needs to be handled by Istio when using wildcard certificates.  This is actually due to a [long standing bug](https://github.com/istio/istio/issues/13589) in Istio where it does not properly tell browsers that they are talking to the wrong host. If this is ever resolved, web and tcp challenges can be created in exactly the same way without any issues.

## k8s-random-port

This challenge type is still for TCP services.  These are for services that cannot be served behind TLS/SNI properly.  The workflow is that CTFd will generate a unique port for each instance in combination with a unique domain name, except that the domain name will not matter in this case.

If UDP/<insert obscure proto here> is needed, the idea is that someone can simply do an OpenVPN port or SSH on the random port and then have players pivot through those.
