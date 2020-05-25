# Corrections to Source Data

VERS="../0.01"

# Add missing line number 
FILE="$VERS/Barwar/Measure for Measure.nena"
echo "Adding missing line number in [$FILE]"
sed -i "" "8 s/^/(1) /" "$FILE"

# Add missing <R> foreign language tag
FILE="$VERS/Urmi_C/The Adventures of a Princess.nena"
echo "Adding missing <R> tag to [$FILE]"
sed -i "" "s/\(ʾe-<R>\*buk̭ḗṱ\*\)/\1<R>/" "$FILE"

# Re-number the lines for a split text
FILE="$VERS/Urmi_C/The Wife Who Learns How to Work (2).nena"
echo "Renumbering lines in $FILE"
python3 reline.py "$FILE"

# add missing prosaic boundaries
SUBPROSA="s/\([ /]*$\)/ˈ\1/" 
FILE="$VERS/Barwar/Qaṭina Rescues His Nephew From Leliθa.nena"
echo "Fixing missing prosody boundaries in $FILE"
sed -i "" "22,26 $SUBPROSA" "$FILE"

FILE="$VERS/Barwar/The Battle With Yuwanəs the Armenian.nena"
echo "Fixing missing prosody boundaries in $FILE"
sed -i "" "18,21 $SUBPROSA" "$FILE"
sed -i "" "65,67 $SUBPROSA" "$FILE"
sed -i "" "69,73 $SUBPROSA" "$FILE"
sed -i "" "86,87 $SUBPROSA" "$FILE"

FILE="$VERS/Barwar/The Sisisambər Plant.nena"
echo "Fixing missing prosody boundaries in $FILE"
sed -i "" "12,18 $SUBPROSA" "$FILE"
sed -i "" "30,33 $SUBPROSA" "$FILE"
sed -i "" "49,51 $SUBPROSA" "$FILE"
