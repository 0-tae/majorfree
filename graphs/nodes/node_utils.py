from graphs.graph_status import GraphStatus
import asyncio

def node(func):
    async def wrapper(state: GraphStatus):
        result = func(state)
        
        if asyncio.iscoroutine(result):
            result = await result
            print_state(func.__name__, result)
            
            return result
        
        print_state(func.__name__, result)
        
        return result
    return wrapper


def print_state(node_name: str, state: GraphStatus):
        print("[node]",node_name,"--->",state)