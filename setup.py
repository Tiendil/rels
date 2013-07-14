# coding: utf-8
import setuptools

setuptools.setup(
    name = 'Rels',
    version = '0.1.0',
    author = 'Aleksey Yeletsky',
    author_email = 'a.eletsky@gmail.com',
    packages = setuptools.find_packages(),
    url = 'https://github.com/Tiendil/rels',
    license = 'LICENSE',
    description = 'library for describing data relations in python (Enums, "relational" tables)',
    long_description = open('README.md').read(),
    include_package_data = True # setuptools-git MUST be installed
)
