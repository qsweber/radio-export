from setuptools import find_packages, setup

setup(
    name='radio-export',
    version='0.0.3',
    description='fill in',
    author='Quinn Weber',
    maintainer='Quinn Weber',
    maintainer_email='quinnsweber@gmail.com',
    packages=find_packages(exclude=('tests',)),
    install_requires=(
        'BeautifulSoup4',
        'requests',
        'typing',
        'Flask',
    ),
)
