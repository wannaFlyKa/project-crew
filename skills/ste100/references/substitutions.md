# Word list

These are words and phrases that the `ste100` skill replaces, each with a simpler word. The list is
our own. It is not the ASD-STE100 dictionary and it does not copy that dictionary. The official
dictionary is free at https://www.asd-ste100.org/.

`scripts/ste_check.py` reads each table row in this file. The first column is the word that the
linter finds. The second column is the fix that the linter prints. The linter also finds the usual
endings of the first word, for example `utilizes` and `utilized`.

A technical name can contain a word from this list. To keep the name, put it in the `--allow` file
of the linter.

## Verbs

| Not STE | Use |
|---|---|
| utilize | use |
| leverage | use |
| employ | use |
| make use of | use |
| perform | do |
| carry out | do |
| execute | run or do |
| commence | start |
| initiate | start |
| kick off | start |
| spin up | start |
| terminate | stop |
| cease | stop |
| retrieve | get |
| obtain | get |
| acquire | get |
| ensure | make sure |
| verify | make sure |
| facilitate | help |
| assist | help |
| attempt | try |
| indicate | show |
| demonstrate | show |
| illustrate | show |
| modify | change |
| alter | change |
| eliminate | remove |
| inform | tell |
| notify | tell |
| determine | find |
| locate | find |
| discover | find |
| transmit | send |
| provide | give |
| establish | make |
| finalize | finish |
| wrap up | finish |
| optimize | improve |
| mitigate | decrease |
| reduce | decrease |
| ramp up | increase |
| clarify | explain |
| elaborate | explain |
| investigate | examine |
| proceed | continue |
| roll out | release |
| prioritize | do first |

## Phrases and connectors

| Not STE | Use |
|---|---|
| in order to | to |
| for the purpose of | to |
| prior to | before |
| subsequent to | after |
| in the event that | if |
| in case of | if there is |
| whether or not | if |
| due to the fact that | because |
| as a result of | because of |
| despite the fact that | but |
| with regard to | about |
| with respect to | about |
| regarding | about |
| in terms of | about |
| as well as | and |
| in addition | also |
| additionally | also |
| furthermore | also |
| moreover | also |
| however | but |
| therefore | so |
| thus | so |
| hence | so |
| consequently | so |
| in the absence of | without |
| in excess of | more than |
| in lieu of | instead of |
| in accordance with | as given in |
| it is important to note that | (delete it) |
| please note that | Note: |
| via | through |
| per | for each |
| versus | compared with |
| e.g. | for example |
| i.e. | that is |
| etc. | (list all items) |
| and/or | A or B, or both |

## Adjectives and adverbs

| Not STE | Use |
|---|---|
| approximately | about |
| numerous | many |
| multiple | many |
| a number of | some |
| a variety of | many |
| the majority of | most |
| various | different |
| sufficient | enough |
| adequate | enough |
| additional | more |
| subsequent | next |
| subsequently | then |
| previously | before |
| currently | now |
| presently | now |
| initially | first |
| initial | first |
| frequently | often |
| occasionally | sometimes |
| primarily | mainly |
| primary | main |
| significant | large or important |
| significantly | much |
| minimal | small |
| optimal | best |
| crucial | important |
| vital | important |
| essential | necessary |
| mandatory | necessary |
| robust | reliable |
| comprehensive | full |
| entire | all |
| straightforward | simple |
| appropriate | correct |
| feasible | possible |
| identical | the same |
| basically | (delete it) |
| essentially | (delete it) |
| actually | (delete it) |
| simply | (delete it) |
| obviously | (delete it) |

## Nouns

| Not STE | Use |
|---|---|
| usage | use |
| functionality | function |
| capability | can (verb) |
| ability to | can |
| able to | can |
| objective | purpose |

## Idioms

| Not STE | Use |
|---|---|
| long pole | longest task |
| low-hanging fruit | easy task |
| out of the box | by default |
| on the fly | at run time |
| under the hood | internally |
| deep dive | detailed examination |
| sanity check | quick check |
| hard-coded | fixed in the code |
| hardcoded | fixed in the code |
| circle back | talk again later |
| touch base | talk |
