from setuptools import setup, find_packages

setup(
    name="pychuck",
    # version="1.0",
    description="Python implementation of the music programming language Chuck.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    license="LICENSE",
    keywords="chuck",
    author="Yikai Li",
    author_email="yikaili@stanford.edu",
    maintainer="Yikai Li",
    maintainer_email="yikaili@stanford.edu",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
    ],
    install_requires=[
        "numpy",
        "networkx",
        "pyaudio",
    ],
    extras_require={
        # 'gui': ["PyQt5"],
        # 'cli': [],
    },
    url="https://github.com/42x00/pychuck.git",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pychuck = pychuck:main",
        ],
        # 'gui_scripts': [
        #     "spam-gui = spam:main_gui",
        # ],
        # 'spam.magical': [
        #     "tomatoes = spam:main_tomatoes",
        # ],
    },
)
