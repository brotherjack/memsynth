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
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO 1 failures found on column 'last_name'
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO On line 2: 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] ERROR HARD failure on the 'nullable' constraint, value='False', with args='None' 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO Data at line is nan
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO 1 failures found on column 'Address_Line_2'
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO On line 1: 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] WARNING soft failure on the 'regex' constraint, value='re.compile('(unit |apt )*[a-z0-9]+|\\\\#*[0-9]+')', with args='{'flags': [2]}' 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO Data at line is Bldg 4
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO 1 failures found on column 'Mobile_Phone'
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO On line 1: 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] ERROR HARD failure on the 'regex' constraint, value='re.compile('^\\d{3}\\-\\d{3}\\-\\d{4}$')', with args='None' 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO Data at line is 4074440909.0
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO 2 failures found on column 'Home_Phone'
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO On line 0: 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] ERROR HARD failure on the 'regex' constraint, value='re.compile('^\\d{3}\\-\\d{3}\\-\\d{4}$')', with args='None' 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO Data at line is 410-5644639, 4105644639
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO On line 2: 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] ERROR HARD failure on the 'regex' constraint, value='re.compile('^\\d{3}\\-\\d{3}\\-\\d{4}$')', with args='None' 
2019-07-04 15:50:14 AspireVX5591G MemSynther[2634] INFO Data at line is 4077217359

```

## Assisting in Development

The maintainers of this project are attempting to stick to Test-Driven Development (as 
best we can :sweat_smile:). If you are unfamiliar with the workflow of TDD, we would ask
that you reference TDD before contributing. A good primer can be found online at Free 
Code Camp [here](https://www.freecodecamp.org/news/test-driven-development-what-it-is-and-what-it-is-not-41fa6bca02a2/).
