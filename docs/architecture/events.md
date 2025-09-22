# Events

## Motivation

While very much a form of pre-mature optimization, we proceed with desigining and building an event & service oriented architecture for the stega suite of financial applications. This is largely because of my own interest and desire to gain experience in building microservice applications; whereas, most of my career experience has been in small monolithic web applications. And so, the following decisions may not always be optimal or perhaps are quite over-engineered, but understand, this is a conscious choice. That said, the following notes serve as a guideline for how we want to handle publishing & consuming events throughout every service in the application.

## Overview

We anticipate workflows that require orchestration between multiple services and in particular a subscription based responsiveness would be useful for updating read views based on new computations (e.g. updated returns, correlations, etc.). And so, we look to a pubsub model for creating loose coupling between orchestrating these cross-service workflows. That is, a service can publish to topics for a given event without having to know what the consuming service actually has to do in response to this. 

As a general rule, we split the workflows of our application into reads & writes where reads follow a CQRS (command query responsibility segragation) pattern and writes follow the event pattern. That is, writes will publish events based on what was submitted and then delegate the responsibility of determining status by having clients subscribe to topics for when an event is resolved.

What does this mean? There are two major outcomes of this:
    
    1. Writes will never return a value. This is really nice for our existing message bus pattern as it does not support returns.
    2. Clients will have a more complex orchestration for any write operations. This generally looks like a) submit command for write operation, b) get response with id of operation/written entity, c) subscribe to topic that listens for associated write operation to resolve, and d) report final result.

### Client Orchestration

A quick further note on the client orchestration is that we will consider having a "boundary" service that abstracts the topic subscription logic from the client. Moreover, to avoid a polling model from the client, we will look into something like web server sockets which has the added benefit of better responsiveness. This also means the CLI client will likely need to implement a local daemon pattern.

### Architecture

Due to a mix of ignorance and just wanting to get started, we will use RabbitMQ to design our event system. And so, a lot of the rest of this discussion will be focuse on concrete aspects of how to setup pubsub queues for events in our system.

Note that every service is wrapped by a REST API but also runs an internal message bus that handles direct commands as well as any resulting propagated events (resulting as a side effect of the command workflows). We can still let the internal message bus handle events, but the handling will be much more light and simply perform a forwarding to a common event exchange that all services can subscribe to. That is, when a new event is collected by a service, rather than dispatch this to an internal service function, this will immediately publish that event to a central broker.

Now how do we allow services to respond or namely subscribe to events. We basically want the same sort of command dispatching each service implements now but as event dispatching that listens for a continuous incoming stream of events. And so, we will now split each service into two runtime containers. One container will continue to serve the REST APIs and command dispatching, while the other container will serve an event subscriber for that service that dispatches incoming events. Note the event dispatching will look eerily similar to the command dispatching of the service and may have parts that can be shared.

And so as a summary we have 3 major architecural components:
    
    1. Shared central broker
    2. Per-service event consumer runtimes
    3. Per-service event publisher runtimes (existing REST API infrastructure)

One last but important thing to cover. How do services know which events to publish and/or subscribe to? The short answer is all events will be defined as dataclasses in the commonly shared `stega_lib` package (e.g. `stega_lib.events`). Each event will also define its topic as a property on the class. And so, each service will only need to know which events it publishes and consumes. As a result a service will not need to know anything about events published or consumed by other services. 

#### Central Broker

Note for the following TODOs there are some RabbitMQ features like "topics", "queues", "routing", "binding", and "exchanges" we will need to iron out where it fits.

TODO: Discuss RabbitMQ and central broker here

#### Per-service event consumer

TODO: Discuss container runtime that continuously listens for incoming events for its subscribed topics
TODO: Discuss how event dispatching will work (e.g. do we create new commands that represent "resolved" events, and then have the event dispatcher just issue that command) or do we just recreate the message bus but for just internal service events

#### Per-service event publisher

TODO: Discuss how the RabbitMQ publishing client works

### Extensions

TODO: Discuss background job executor that could be brokered via RabbitMQ for each service to immediately provide responses
