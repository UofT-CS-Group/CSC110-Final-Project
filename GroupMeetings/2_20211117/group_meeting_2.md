# Project Instruction

## Written Report

- Citation / Reference Issues
    - [Inline Reference](https://advice.writing.utoronto.ca/using-sources/documentation/)

## Program

- We need to write an automation to automatically download our datasets from the Internet and put them into correct folders.
- `doctest` and `python_ta` sucks!
- We need a `requirement.txt` to specify the library we used.
    - We could use Windows Sandbox to simulate a brand new windows computer.
    - We could use WSL to simulate a Linux environment.
    - But we need to also test our program on Mac OS.

# My Plan for Our Program

## Significance 

- I don't think our program really analyze, predict, or help us understand something.
- Currently, our program just display the COVID trend and the school closure trend.
- But we don't know the potential factors that caused (correlated) with those trends.
- So, we need some sort of statistical analysis to make our program meaningful, although we are doing the CS final project.

## Infrastructure and Style

- Our program may exceeds 2000+ lines of code, so we really need to further divide our program to make it tidy.
- All non-source files should go resources/ folder.

## TODO

- [ ] Better visualization.
    - Line style, legend, title, ...
    - More types of graph, not only scatterplot.
    - Let user choose line color, line style, font, even languages...
- [ ] Table View
    - It could be not plausible because our we have too many data.
    - But we need to try to do that.

- [ ] Let user choose different algorithm to display the influence of time complexity.
    - This should be happened on the Initialization Window.

- [ ] Better performance
    - **Data Initializing**
        1. Multi IO threads.
        2. Progressive loading
        3. Better algorithms
    - Crosshair on graphs
        - Use `blitting`
    - Confirm button
- [ ] **Better layout** 

- [ ] Advanced Option: Machine learning and linear regression analysis
- [ ] Advanced Option: Beautiful UI
- [ ] Advanced Option: Font-backend separation
    - Now we have all functionalities (frontend + backend) in `gui.py`.