class MicroService:
    def __init__(self, start_port: int, instances: int, prefix: str) -> None:
        '''
        This microservice object provides functionality for managing a pool of
        instances that represent actual running instances.


        Params:

        start_port - the lowest port number that this service starts at.
        
        instances - the number of instances this microservice will begin with.

        prefix - the common part of the URL that all endpoints for this service
            will share.
        '''

        self.__prefix = prefix
        self.__start_port = start_port
        self.__max_inst = instances
        self.__pool = [ (self.__start_port + i) for i in range(self.__max_inst) ]
        self.__curr = 0

    def remove_instance(self, port: int) -> None:
        ''' Remove a port number from the pool. The port represents an instance. '''
        self.__pool.remove(port)
        # If current index is not out of bounds, reset to zero
        if self.__curr >= len(self.__pool):
            self.__curr = 0

    def get_prefix(self) -> str:
        ''' Get the endpoint prefix for this microservice. '''
        return self.__prefix

    def get_instance(self) -> int:
        ''' Return a port number representing an instance of the microservice.
            If no instances are available, returns -1. '''

        # If pool is empty, retrun -1
        if len(self.__pool) == 0:
            return -1
        # Else get the port at the current index and increment current index
        else:
            port = self.__pool[self.__curr]
            self.__curr = (self.__curr + 1) % len(self.__pool)
            return port

    def get_pool(self) -> list:
        ''' Return a list representation of this microservice's worker pool. '''
        return self.__pool

class MicroServiceManager:
    def __init__(self, services_config):
        '''
        The service manager is used to manage service worker pools.
        A worker in this context refers to an instance of the microservice.
        Takes a service config object defined as:
        
        {
            <service_name>: {
                "PREFIX": <prefix_of_URL>
                "PORT": <starting_port>,
                "INSTANCES": <num_instances>
            },
            ...
        }
        '''

        self.__services = {}
        for svc_key in services_config:
            svc_cfg = services_config[svc_key]
            prefix = svc_cfg["PREFIX"]
            start_port = svc_cfg["PORT"]
            instances = svc_cfg["INSTANCES"]
            self.__services[svc_key] = MicroService(start_port, instances, prefix)


    def remove_worker(self, service_key: str, port: int) -> None:
        ''' Remove the worker of the given service type/key with the given port. '''
        self.__services[service_key].remove_instance(port)

    def get_worker(self, service_key) -> int:
        ''' Get a port of a running instance of the specified type/key. '''
        return self.__services[service_key].get_instance()

    def get_pools(self) -> dict:
        ''' Returns a dictionary representation of the service worker pools,
            where the pool for each service is represented as a list.'''

        pools = {}
        for svc_key in self.__services:
            pools[svc_key] = self.__services[svc_key].get_pool()
        return pools

    def get_service_type(self, endpoint) -> str:
        ''' Returns the service key/type associated with the given endpoint.
            If no services match the endpoint, returns an empty string. '''
        
        for svc_key in self.__services:
            prefix = self.__services[svc_key].get_prefix()
            # If there's a match at index 0, return the service type/key
            if endpoint.find(prefix) == 0:
                return svc_key
        
        # No matches
        return ""