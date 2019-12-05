# coding: utf-8
import setuptools

setuptools.setup(
    name='Rels',
    version='0.3.1',
    description='Library for describing data relations in python (Enums, "relational" tables)',
    long_description = open('README.rst').read(),
    url='https://github.com/Tiendil/rels',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Natural Language :: English',
        'Natural Language :: Russian'],
    keywords=['enums', 'data relations', 'relational tables'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    test_suite = 'tests',
    )
