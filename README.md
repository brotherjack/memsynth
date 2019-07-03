# memsynth
Florida DSA's rad dialectical tool for synthesizing membership lists

## Project Idea and Goals

The project initially was devised with the goal of cleaning and managing local chapters 
memebrship lists. A longer term goal is to allow users of local chapters to not only 
clean and maintain a database of local users, but to also better coordinate list 
distribution between national DSA and locals, and between locals and members. See the
project's [milestones](https://github.com/brotherjack/memsynth/milestones) section for 
more information.

## Installation

### Requirements

 - Python >= 3.6

Additional requirements are in the `requirements.txt`. We highly recommend that you install 
a Python virtualenv and load these requirements into the active virtualenv with the 
customary `pip install -r requirements.txt`.

## Use Cases

### Check your membership list against your epectations, and find out what you need to fix

```python
from memsynth.main import MemSynther
msy = MemSynther()

# Load the expectations and the memebership list
msy.load_expectations_from_json("tests/params.json")
msy.load_from_excel("tests/fakeodsa.xlsx")

# Check to make sure it conforms to those expectations...it won't :/

if not msy.check_membership_list_on_parameters(strict=True):
    msy.report_failures()
```

#### Example output >>>

```
1 failures found on column 'last_name'
On line 2: 
	- HARD failure on the 'nullable' constraint, value='False', with args='None' 
Data at line is nan

1 failures found on column 'Mobile_Phone'
On line 1: 
	- HARD failure on the 'regex' constraint, value='re.compile('^\\d{3}\\-\\d{3}\\-\\d{4}$')', with args='None' 
Data at line is 4074440909.0

2 failures found on column 'Home_Phone'
On line 0: 
	- HARD failure on the 'regex' constraint, value='re.compile('^\\d{3}\\-\\d{3}\\-\\d{4}$')', with args='None' 
Data at line is 410-5644639, 4105644639
On line 2: 
	- HARD failure on the 'regex' constraint, value='re.compile('^\\d{3}\\-\\d{3}\\-\\d{4}$')', with args='None' 
Data at line is 4077217359
```

## Assisting in Development

The maintainers of this project are attempting to stick to Test-Driven Development (as 
best we can :sweat_smile:). If you are unfamiliar with the workflow of TDD, we would ask
that you reference TDD before contributing. A good primer can be found online at Free 
Code Camp [here](https://www.freecodecamp.org/news/test-driven-development-what-it-is-and-what-it-is-not-41fa6bca02a2/).


