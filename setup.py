import setuptools

setuptools.setup(
    name="ftl",
    version="0.0.1",
    author="Theo Breuer-Weil",
    author_email="theobreuerweil@gmail.com",
    description="For fetching and transforming data",
    url="https://github.com/somemarsupials/ftl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'tornado'
    ]
)
