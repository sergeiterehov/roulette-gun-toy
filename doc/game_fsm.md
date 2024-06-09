# Игровой КА

```mermaid
stateDiagram-v2
  [*] --> IDLE : begin
  IDLE --> MASTER_SELECTION : start
  MASTER_SELECTION --> SHUTTING : select_master
  SHUTTING --> EXTRACTING : shut
  EXTRACTING --> EMPTY_MAGAZINE : eject
  EXTRACTING --> SHUTTING : eject
  EMPTY_MAGAZINE --> SHUTTING : reload
  SHUTTING --> DONE : game_over
```
