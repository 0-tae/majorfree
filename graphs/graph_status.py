from typing import TypedDict, Annotated, List, Dict, Any
import operator


class GraphStatus(TypedDict):
    messages: Annotated[List[Dict[str, Any]], operator.add]
    answer: str   
    instruction: str
    
    search_type: str
    optional_args: Dict[str, Any]
    context_relrelevant_score: float
    remaining_steps: int
