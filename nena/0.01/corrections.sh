# Corrections to Source Data

# Add missing line number 
MEASUREFORME="Barwar/Measure For Measure.nena"
echo "Adding missing line number in [$MEASUREFORME]"
sed -i "" "8 s/^/(1) /" "$MEASUREFORME"

PRINCESSAD="Urmi_C/The Adventures Of A Princess.nena"
echo "Adding missing <R> tag to [$PRINCESSAD]"
sed -i "" "s/\(ʾe-<R>\*buk̭ḗṱ\*\)/\1<R>/" "$PRINCESSAD"
