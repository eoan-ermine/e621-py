import setuptools

setuptools.setup(
    name="e621", # Replace with your own username
    version="0.1.0",
    author="PatriotRossii",
    author_email="patriotrossii2019@mail.ru",
    long_description="e621.net API wrapper written in Python",
    description="e621.net API wrapper written in Python",
    url="https://github.com/PatriotRossii/e621-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)