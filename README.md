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

```python
from memsynth.main import MemSynther
msy = MemSynther()

# Load the expectations and the memebership list
msy.load_expectations_from_json("tests/params.json")
msy.load_from_excel("tests/fakeodsa.xlsx")

# Check to make sure it conforms to those expectations...it won't :/
from memsynth import exceptions
try:
    msy.verify_memlist_data_integrity()
except exceptions.MembershipListIntegrityExcepton:
    # Check failures
    for fail_column in msy.failures.keys():
        print(
            f"{len(msy.failures[fail_column].fails)} failures found on "
            f"column '{fail_column}'"
        )
        for failure in msy.failures[fail_column].fails:
            print(f"On line {failure.line}: ")
            for param in failure.why:
                print(
                    f"\t- {'soft' if param.soft else 'HARD'} "
                    f"failure on the '{param.name}' constraint, "
                    f"value='{param.value}', with args='{param.args}' "
            )
            print(f"Data at line is {failure.data}")
        print("")
```

## Assisting in Development

The maintainers of this project are attempting to stick to Test-Driven Development (as 
best we can :sweat_smile:). If you are unfamiliar with the workflow of TDD, we would ask
that you reference TDD before contributing. A good primer can be found online at Free 
Code Camp [here](https://www.freecodecamp.org/news/test-driven-development-what-it-is-and-what-it-is-not-41fa6bca02a2/).


