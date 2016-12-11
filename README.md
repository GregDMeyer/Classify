## Classify

Modified version from Hull-Lab's bringing classify and specify into one program.

Allows classification of damage level and taxon ID all at once.

New in version 0.1:

 - Use arrow keys to move back and forth between images
    - Any previous input shows up!
 - Data automatically saved whenever switching to a different image
 - Remove confidence for damage level (let me know if that should be changed, but it seems silly to ask how confident you are in the damage level. Isn't it pretty clear)
 - Keep track of username to know who did the classifying
 - Can pass path to image directory on the command line, so you don't have to use the file dialog. Example usage: `python classify.py /home/greg/my_awesome_limpet_images`
 - Option to ignore (skip) images that already have all fields filled out. This generalizes the old "start where you left off" feature.
 
 ---

####To do:

 - Additional information, like encrusters, predation, etc.
 - Support for filtering species based on age
 - Full set of command line options, such as whether to ask for additional information, whether to skip images with complete data, etc.
 
 ---
 
 Please let me know of any bugs/ideas! (see 'Issues' tab on github!)