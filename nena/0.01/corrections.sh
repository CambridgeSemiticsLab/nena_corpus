# Corrections to Source Data

# Add missing line number 
MEASUREFORME="Barwar/Measure For Measure.nena"
echo "Adding missing line number in [$MEASUREFORME]"
sed -i "" "8 s/^/(1) /" "$MEASUREFORME"
