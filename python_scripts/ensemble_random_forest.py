# %% [markdown]
# # Random forests
#
# In this notebook, we will present the random forest models and show the
# differences with the bagging ensembles.
#
# Random forests are a popular model in machine learning. They are a
# modification of the bagging algorithm. In bagging, any classifier or
# regressor can be used. In random forests, the base classifier or regressor
# must be a decision tree.
#
# Random forests have another particularity: when training a tree, the search
# for the best split is done only on a subset of the original features taken at
# random for each split.
#
# Therefore, random forests are using randomization on both axes of the data
# matrix:
#
# - by bootstrapping samples for each tree in the forest;
# - randomly selecting a subset of features at each node of the tree.
#
# ## A look at random forests
#
# We will illustrate the usage of a random forest classifier on the adult
# census dataset.

# %%
import pandas as pd

adult_census = pd.read_csv("../datasets/adult-census.csv")
target_name = "class"
data = adult_census.drop(columns=[target_name, "education-num"])
target = adult_census[target_name]

# %% [markdown]
# ```{note}
# If you want a deeper overview regarding this dataset, you can refer to the
# Appendix - Datasets description section at the end of this MOOC.
# ```

# %%[markdown]
#
# The adult census contains some categorical data and we will encode the
# categorical features using an `OrdinalEncoder` since we are going to use
# tree-based models.
#
# Since we can get rare category during cross-validation, we use specify the
# option to handle the unknown categories after training.

# %%
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import make_column_transformer, make_column_selector

categorical_encoder = OrdinalEncoder(
    handle_unknown="use_encoded_value", unknown_value=-1
)
preprocessor = make_column_transformer(
    (categorical_encoder, make_column_selector(dtype_include=object)),
    remainder="passthrough"
)

# %% [markdown]
#
# We will first give a simple example where we will train a decision tree
# classifier and check its statistical performance via cross-validation.
# We need to use a scikit-learn pipeline such that we first preprocess the
# dataset to only have numerical data at the entry of the decision tree.

# %%
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier

tree = make_pipeline(preprocessor, DecisionTreeClassifier(random_state=0))

# %%
from sklearn.model_selection import cross_val_score

scores_tree = cross_val_score(tree, data, target)

print(f"Decision tree classifier: "
      f"{scores_tree.mean():.3f} +/- {scores_tree.std():.3f}")

# %% [markdown]
#
# In the previous notebook, we should how to use a bagging model. Indeed, we
# need to specificy the base model to use, here a decision tree classifier. In
# addition, we need to specify how many models do we want to combine. Note that
# we also need to preprocess the data and thus use a scikit-learn pipeline.

# %%
from sklearn.ensemble import BaggingClassifier

bagged_trees = make_pipeline(
    preprocessor,
    BaggingClassifier(
        base_estimator=DecisionTreeClassifier(random_state=0),
        n_estimators=50, n_jobs=2, random_state=0,
    )
)

# %%
scores_bagged_trees = cross_val_score(bagged_trees, data, target)

print(f"Bagged decision tree classifier: "
      f"{scores_bagged_trees.mean():.3f} +/- {scores_bagged_trees.std():.3f}")

# %% [markdown]
#
# Now, we will use a random forest. You will observe that we do not need to
# specify any `base_estimator` because the estimator is forced to be a
# decision tree. Thus, we only have to specify the desired number of trees in
# the forest.

# %%
from sklearn.ensemble import RandomForestClassifier

random_forest = make_pipeline(
    preprocessor,
    RandomForestClassifier(n_estimators=50, n_jobs=2, random_state=0)
)

# %%
scores_random_forest = cross_val_score(random_forest, data, target)

print(f"Random forest classifier: "
      f"{scores_random_forest.mean():.3f} +/- "
      f"{scores_random_forest.std():.3f}")

# %% [markdown]
#
# It seems that the random forest is performing slightly better than the bagged
# trees possibly due to the randomized selection of the features which
# decorrelates the prediction errors of individual trees and as a consequence
# make the averaging step more efficient at reducing overfitting.
#
# ## Details about default hyperparameters
#
# For random forests, it is possible to control the amount of randomness for
# each split by setting the value of `max_features` hyperparameter:
#
# - `max_feature=0.5` means that 50% of the features are considered at each
#   split;
# - `max_features=1.0` means that all features are considered at each split
#   which effectively disables feature subsampling.
#
# By default, `RandomForestRegressor` disables feature subsampling while
# `RandomForestClassifier` uses `max_features=np.sqrt(n_features)`. These
# default values reflect good practices given in the scientific literature.
# However, `max_features` is one of the hyperparameter to consider when tuning
# a random forests.
#
# Note that bagging ensemble exposes a parameter `max_features` as well.
# However, the process is different since the base estimator is not necessarily
# a decision tree. Indeed, the features subsampling take place at the model
# level by selecting a subset of feature on each bootstrap sample.
#
# We summarize these details in the following table:
#
# | Ensemble model class     | Base model class          | Default value for `max_features` | Level of features subsampling |
# |--------------------------|---------------------------|----------------------------------|-------------------------------|
# | `BaggingClassifier`      | User specified (flexible) | `n_features` (no subsampling)    | Model level                   |
# | `RandomForestClassifier` | `DecisionTreeClassifier`  | `sqrt(n_features)`               | Tree node level               |
# | `BaggingRegressor`       | User specified (flexible) | `n_features` (no subsampling)    | Model level                   |
# | `RandomForestRegressor`  | `DecisionTreeRegressor`   | `n_features` (no subsampling)    | Tree node level               |
