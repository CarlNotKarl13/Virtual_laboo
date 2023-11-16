import rpy2.robjects as robjects

# Define an R function
r_function = """
square <- function(x) {
  return(x^2)
}
"""

# Evaluate the R function
robjects.r(r_function)

# Call the R function from Python
result = robjects.r['square'](5)

# Print the result
print(result)s