"""
Constant values
"""

# paths
folderLocation = "/home/mikkel/Documents/AuthorAttribution/"
location = folderLocation + "src/data/"
authors = location + "Authors/"
corpora = location + "Corpora/"
tests = location + "Tests/"
tableSave = folderLocation + "report/tabeller/"
resultDir = location + "Results/"

#The number of posts
fewPosts = (35, 68)
somePosts = (69, 102)
manyPosts = (103, 9999)

#Wrappers to ensure that the definitions of short, medium etc. remain
#consistent
shortLength = (0, 100)
mediumLength = (100, 1000)
longLength = (1000, 3000)
rantLength = (3000, 9999999)
