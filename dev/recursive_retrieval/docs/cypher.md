# Recursive Retrieval Cyphers

## Getting Subraph Based on Entity ID
    MATCH p = (:Entity { id: "Harry" })-[*]->()
    RETURN p;

- the  `*` means traversing all paths
- adding a number, `x`, after `*` means a max hop distance of only that many nodes 
- can search labels by replacing `Entity` with labels
- `->` can be replaced with `<-` for incoming children or `-` for both outgoing and incoming children


<img src="images/harry_subgraph.png" alt="drawing" width="500"/>
