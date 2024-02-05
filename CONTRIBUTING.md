# Contributing Guidelines

## Before Contributing

Welcome to [strimzi-kafka-cli](https://github.com/systemcraftsman/strimzi-kafka-cli)! Before sending your pull requests, make sure that you __read the whole guidelines__. If you have any doubt about the contributing guide, please feel free to [state it clearly in an issue](https://github.com/systemcraftsman/strimzi-kafka-cli/issues/new).

## Contributing

### Contributor

We are very happy that you are considering implementing algorithms and data structures for others! This repository is referenced and used by learners from all over the globe. Being one of our contributors, you agree and confirm that:

- Your work will be distributed under [Apache-2.0](LICENSE.md) once your pull request is merged
- Your submitted work fulfils or mostly fulfils our styles and standards

__New implementation__ is welcome! For example, new solutions for a problem, different representations for a graph data structure or algorithm designs with different complexity but __identical implementation__ of an existing implementation is not allowed. Please check whether the solution is already implemented or not before submitting your pull request.

__Improving comments__ and __writing proper tests__ are also highly welcome.

### Contribution

We appreciate any contribution, from fixing a grammar mistake in a comment to implementing complex algorithms. Please read this section if you are contributing your work.

Your contribution will be tested by our [automated testing on Github CI/CD](https://github.com/SystemCraftsman/strimzi-kafka-cli/actions) to save time and mental energy.  After you have submitted your pull request, you should see the Github CI/CD tests start to run at the bottom of your submission page.  If those tests fail, then click on the ___details___ button and try to read through the Github CI/CD output to understand the failure.  If you do not understand, please leave a comment on your submission page and a community member will try to help.

Please help us keep our issue list small by adding fixes: #{$ISSUE_NO} to the commit message of pull requests that resolve open issues. GitLab will use this tag to auto-close the issue when the PR is merged.

## Getting Started with Development

### Cloning the Repository

To start your development journey, you will need to clone the repository from Github. Cloning a repository creates a local copy of the project on your machine, allowing you to make changes and contribute to the codebase.

Follow these steps to clone the repository:

1. Open your web browser and navigate to the repository on Github.
2. On the repository page, click on the Fork button in the top-right corner. This will create a personal copy of the repository under your GitLab account.
3. Once the repository is forked, go to your GitLab profile and navigate to the forked repository.
4. Click on the "Clone" button for clone to repository.
5. Copy the URL provided in the cloning options. It should look like https://github.com/your-username/strimzi-kafka-cli.git.
6. Open your terminal or command prompt on your local machine.
7. Navigate to the directory where you want to clone the repository using the cd command. For example, to navigate to your home directory, you can use cd ~.
8. In the terminal, enter the following command to clone the repository:

```bash
git clone https://github.com/your-username/strimzi-kafka-cli.git
```
Replace `your-username` with your GitLab username.

9. Press Enter to execute the command. Git will now download the repository and create a local copy on your machine.

10. Once the cloning process is complete, you can navigate into the cloned repository using the cd command. For example:

```bash
cd strimzi-kafka-cli
```

Congratulations! You have successfully cloned the repository and are ready to start development. In the next sections, we will cover the setup and configuration steps required for your development environment.



### Pre-commit Tool

This project utilizes the [pre-commit](https://pre-commit.com/) tool to maintain code quality and consistency. Before submitting a pull request or making any commits, it is important to run the pre-commit tool to ensure that your changes meet the project's guidelines.

To run the pre-commit tool, follow these steps:

1. Install pre-commit by running the following command: `poetry install`. It will not only install pre-commit but also install all the deps and dev-deps of project

2. Once pre-commit is installed, navigate to the project's root directory.

3. Run the command `pre-commit run --all-files`. This will execute the pre-commit hooks configured for this project against the modified files. If any issues are found, the pre-commit tool will provide feedback on how to resolve them. Make the necessary changes and re-run the pre-commit command until all issues are resolved.

4. You can also install pre-commit as a git hook by execute `pre-commit install`. Every time you made `git commit` pre-commit run automatically for you.

### Coding Style

We want your work to be readable by others; therefore, we encourage you to note the following:

- Please write in Python 3.8. For instance:  `print()` is a function in Python 3 so `print "Hello"` will *not* work but `print("Hello")` will.
- Please focus hard on the naming of functions, classes, and variables.  Help your reader by using __descriptive names__ that can help you to remove redundant comments.
  - Single letter variable names are *old school* so please avoid them unless their life only spans a few lines.
  - Expand acronyms because `gcd()` is hard to understand but `greatest_common_divisor()` is not.
  - Please follow the [Python Naming Conventions](https://pep8.org/#prescriptive-naming-conventions) so variable_names and function_names should be lower_case, CONSTANTS in UPPERCASE, ClassNames should be CamelCase, etc.

- We encourage the use of Python [f-strings](https://realpython.com/python-f-strings/#f-strings-a-new-and-improved-way-to-format-strings-in-python) where they make the code easier to read.

### Conventional Commits

To maintain a consistent commit message format and enable automated release management, we follow the Conventional Commits specification. Please adhere to the following guidelines when making commits:

- Use the format: `<type>(<scope>): <description>`

  - `<type>`: Represents the type of change being made. It can be one of the following:
    - **feat**: A new feature
    - **fix**: A bug fix
    - **docs**: Documentation changes
    - **style**: Code style/formatting changes
    - **refactor**: Code refactoring
    - **test**: Adding or modifying tests
    - **chore**: Other changes that don't modify code or test cases

  - `<scope>`: (Optional) Indicates the scope of the change, such as a module or component name.

  - `<description>`: A concise and meaningful description of the change.

- Separate the type, scope, and description with colons and a space.

- Use the imperative mood in the description. For example, "Add feature" instead of "Added feature" or "Adding feature".

- Use present tense verbs. For example, "Fix bug" instead of "Fixed bug" or "Fixes bug".

- Start the description with a capital letter and do not end it with a period.

- If the commit addresses an open issue, include the issue number at the end of the description using the `#` symbol. For example, `fix(user): Resolve login issue #123`.

Example commit messages:

- `feat(user): Add user registration feature`
- `fix(auth): Fix authentication logic`
- `docs(readme): Update project documentation`
- `style(css): Format stylesheets`
- `refactor(api): Simplify API endpoints`
- `test(utils): Add test cases for utility functions`

By following these guidelines, we can maintain a clear and meaningful commit history that helps with code review, collaboration, and automated release processes.
