# Entity Scripting Language

## Purpose
This language aims to support modding features for games using Entity-Component-Systems by providing a C-like programming language

## Target Users
Game developers, game modders. Expected to be proficient in the procedural inner workings of a C-like language.

## Design Principles
1. Data-Driven
2. Sandboxed & Type Safe
4. Robust familiarity with C features

## Initial Features
1. C Structures supported out of the box
2. Decorator "@system" tells the compiler that:
  a. a function should be a registered system
  b. it serves as one (of many) entry points into execution 
4. "const" and "mut" keywords tell the compiler to enforce certain access patterns and hint the interpretter as to what order systems are to be executed
5. References are the type-safe boundary between bytecode and the interpretter. They *always* point to a valid instance!
6. Functions return by value to prevent RCEs




## Week 1 Run
```bash
python main.py
```
