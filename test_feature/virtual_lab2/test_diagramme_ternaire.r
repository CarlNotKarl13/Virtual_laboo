library("Ternary")

par(mar = rep(0.2, 4))
TernaryPlot(axis.labels = seq(0, 10, by = 1))

nPoints <- 4000L
coordinates <- cbind(abs(rnorm(nPoints, 2, 3)),
                     abs(rnorm(nPoints, 1, 1.5)),
                     abs(rnorm(nPoints, 1, 0.5)))

# Colour plot background
ColourTernary(TernaryDensity(coordinates, resolution = 10L))

# Add points
TernaryPoints(coordinates, col = "red", pch = ".")

# Contour by point density
TernaryDensityContour(coordinates, resolution = 30L)