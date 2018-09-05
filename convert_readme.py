import pypandoc


with open("README.md") as f:
    # Convert markdown file to rst
    markdown = f.read()

    #converts markdown to reStructured
    z = pypandoc.convert(markdown,'rst',format='markdown')

    #writes converted file
    with open('README.rst','w') as outfile:
        outfile.write(z)
