# TODO:
Main Deus Flow routing:
- Revise all prompts, they are all made by AI and they suck (too long and can cause low importance weight per token -> Not following instructions)
- Refactor and regroup the ContextManager methods as they dont need to be bundle up toghether because the ContextManager concept might not be solid

- Figure out a way to exit the question refinement process (too tidious): Either with some control switch for the user, figure out a way for the AI to know when to stop (prompt? some limit?) or both?
- In the case that it finishes the establish scope with not enough information for practical implementation, execute a process to fill in the gaps with educated guesses wherever needed (most likely will come to small technical implentation gap filling which will be totally fine to guess, and if not then implement a flow for user confirmatio on the worst cases)

- Finish implementing _merge_requirements() method

- Figure out monitoring
- Figure out how the data will be stored (Dictionaries? Also feedback might just be a key value pair instead of a field of the DataBundle class)

Late Game:
- Implement Weaviate DB (for semantic search functions)
- Figure out a format for tools and how to monitor their execution
- Populate toolkit (at least the core tools)
- Figure out a way to implement Wisdom/Learned Lessons
