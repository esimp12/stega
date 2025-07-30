- [ ] Setup integration tests for portfolio service
- [ ] Update database migration for new schema changes (just blow up existing scipts and start fresh)


- [ ] Setup external event system for portfolio service 
    - Use RabbitMQ
    - Producer as its own service that registers a topic exchange for events
    - Move events to common package (stega_lib)
    - Consumer in each service that runs in separate container

- [ ] Setup following CLI commands that run through stega core
    - `stega portfolio list`
    - `stega portfolio create --name <name> --assets <symbol>:<weight>,<symbol>:<weight>`
    - `stega portfolio create --portfolio-file <file>`
    - `stega portfolio update --id <id> --name <name> --assets <symbol>:<weight>,<symbol>:<weight>`
    - `stega portfolio update --id <id> --portfolio-file <file>`
    - `stega portfolio delete --id <id>`
    - `stega portfolio get --id <id>`

    - For the create commands etc. we want to subscribe to the appropriate event and then display the result when completed

# NOTES

- What is the application core?
    - The core is akin to the gateway in the microservices architecture. It is the entry point for all external facing requests and handles routing to the appropriate service.
    - As a result, the core has no persistence layer, as this ultimately gets handed off to each service. And so, the core design can be slightly different with no unit of work or repository pattern.
    - Instead, the core will have a set of service ports that know how to interact with each service. The core will still have a message bus that allows it to process events and send commands to the appropriate service. The core will also have event listeners that can handle external events when they occur and handle them appropriately.

- Do we really need the core?
    - Can we just have the clients talk to each service directly?
    - Yes, but each client would need to know when certain interactions require data from multiple services to interact correctly.