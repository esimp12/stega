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

Due to a mix of ignorance and just wanting to get started, we will use RabbitMQ to design our event system. And so, a lot of the rest of this discussion will be focus on concrete aspects of how to setup pubsub queues for events in our system.

Note that every service is wrapped by a REST API but also runs an internal message bus that handles direct commands as well as any resulting propagated events (resulting as a side effect of the command workflows). We can still let the internal message bus handle events, but the handling will be much more light and simply perform a forwarding to a common event exchange that all services can subscribe to. That is, when a new event is collected by a service, rather than dispatch this to an internal service function, this will immediately publish that event to a central broker.

Now how do we allow services to respond or namely subscribe to events? We basically want the same sort of command dispatching each service implements now but as event dispatching that listens for a continuous incoming stream of events. And so, we will now split each service into two runtime containers. One container will continue to serve the REST APIs and command dispatching, while the other container will serve an event subscriber for that service that dispatches incoming events. Note the event dispatching will look eerily similar to the command dispatching of the service and may have parts that can be shared.

And so as a summary we have 3 major architecural components:
    
1. Shared central broker
2. Per-service event consumer runtimes
3. Per-service event publisher runtimes (existing REST API infrastructure)

One last but important thing to cover. How do services know which events to publish and/or subscribe to? The short answer is all events will be defined as dataclasses in the commonly shared `stega_lib` package (e.g. `stega_lib.events`). Each event will also define its topic as a property on the class. And so, each service will only need to know which events it publishes and consumes. As a result a service will not need to know anything about events published or consumed by other services. 

#### Central Broker

For the central broker, we don't need to create any application code, we just need to make the rabbitmq runtime available to all services we expect to use it. Given we are using docker-compose for deploying our services, this may look as follows:

```
broker:
  image: rabbitmq:latest
  hostname: broker
  restart: always
  environment:
    RABBITMQ_DEFAULT_USER: test
    RABBITMQ_DEFAULT_PASS: test
  volumes:
    - broker_data:/var/lib/rabbitmq

volumes:
  broker_data:

```

We can easily improve this infrastructure definition by adding a service health check, broker network, service links, etc. 

Note for some reason the rabbitmq maintainers decided to stop supporting `_FILE` type envvars which allows us to be able to set the user/pass pair from Docker secrets in a simple way. However, there appears to be a [workaround](https://github.com/docker-library/rabbitmq/issues/141#issuecomment-1488134628).

#### Exchange

Note that the initial expected event workflows in our system will be rather simple - if event A occurs, then have event handler A respond to just that. That is, an event firing captures all the information we need with no additional context influencing how its handled (e.g. an event fired from service A should have an identical response to an event fired from service B).

This makes using a "direct" exchange the simplest and most natural. Each event will define its own unique `routing_key`. When events are published we can know where to send them by this class property on the event objects, and consuming services will know upfront the event classes it needs to subscribe to, so again we can look to this class property. Note we could pretty simply migrate to a "topic" exchange by designing our `routing_keys` appropriately (e.g. we could prepend the service name to the event, `serviceA.events.event1`, and then listen to topics of `*.events.event1` or by service where appropriate).

So what do the producers and consumers look like? 

##### Producers

Each service may operate as a producer. To start, these publishing calls will be synchronous. That is, we open a connection to the broker, we publish any events to the direct exchange using each event's unique `routing_key`, and then we close the conneciton. This could look as follows:

```
conn = pika.BlockingConnection(...)
channel = conn.channel()
channel.exchange_declare(exchange="events", exchange_type="direct")
for event in events:
    channel.basic_publish(exchange="events", routing_key=event.routing_key, body=event.message)
conn.close()
```

Note there's a few optimizations and improvements we'll want to make or consider here. To name a couple, 1) use a connection pool or 2) have all event publishing on its own background thread and/or process.

##### Consumers

Each service may operate as a consumer. A service will know beforehand, statically set by source, which events it needs to listen for. Since consumers need to listen, this will run as a blocking process in another container runtime defined by that service's docker compose specification. And then this blocking call will delegate the actual handling of events to an internal message bus which we will likely want to run in a background thread or process. That is, we open a blocking connection to the broker, we create a *single* nondurable queue for the service (we don't care about previous events, just new ones), we create queue bindings for each event type we expect to recieve, and finally we consume messages on the service's queue. This could look as follows:

```
conn = pika.BlockingConnection(...)
channel = conn.channel()
channel.exchange_declare(exchange="events", exchange_type="direct")
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue
for event_type in event_types:
    channel.queue_bind(exchange="events", queue=queue_name, routing_key=event_type.routing_key)

def callback(ch, method, properties, body):
    event = Event.create(method.routing_key, body)
    dispatch(event)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
```
