"""Week 1 project identity configuration."""


LANGUAGE_NAME = "Entity Shader Language"
AUTHOR = "Devin Frost"
VERSION = "0.1"
DESCRIPTION = "Entity Shader Language (ESL) is a C-Like shader language built for modding" 

# tests
POSITIVES = ["ESL_sources/positives.esl"]
NEGATIVES =  ["ESL_sources/negatives.esl"]
GRAMMAR_PATH = "grammar.lark"
SPLITTER = "/**/"
