# Complex Queries

## Given a set of courses, find all the possible combinations of courses that are required to complete it.

courses: the initial sets of courses

1. for each course, find all the possible combinations of courses that are required to complete it
2. take a combination of all the possible unions

Example:

CSE 304 -> AND( OR( CSE216, CSE260 ), CSE 220 )

CSE 327 -> AND( OR( CSE214, CSE230, CSE260 ), OR( AMS210, MAT211 ) )