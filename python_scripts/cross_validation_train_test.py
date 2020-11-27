# %% [markdown]
# # Train and test datasets
# Before discussing the cross-validation framework, we will linger on the
# reasons for always having training and testing sets. Let's first look at the
# limitation of using a unique dataset.
#
# To illustrate the different concepts, we will use the california housing
# dataset.

# %%
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing(as_frame=True)
X, y = housing.data, housing.target

# %% [markdown]
# We recall that in this dataset, the aim is to predict the median value of
# houses in an area in California. The feature collected are based on general
# real-estate and geographical information.

# %%
print(housing.DESCR)

# %%
X.head()

# %% [markdown]
# To simplify future visualization, we transform the target in k\$.

# %%
y *= 100
y.head()

# %% [markdown]
# ## Empirical error vs generalization error
#
# As mentioned previously, we start by fitting a decision tree regressor on the
# full dataset.

# %%
from sklearn.tree import DecisionTreeRegressor

regressor = DecisionTreeRegressor()
regressor.fit(X, y)

# %% [markdown]
# After training the regressor, we would like to know the regressor's potential
# performance once deployed in production. For this purpose, we use the mean
# absolute error, which gives us an error in the native unit, i.e. k\$.

# %%
from sklearn.metrics import mean_absolute_error

y_pred = regressor.predict(X)
score = mean_absolute_error(y_pred, y)
print(f"In average, our regressor make an error of {score:.2f} k$")

# %% [markdown]
# A perfect prediction is with no error is too optimistic and almost always
# revealing a methodological problem when doing machine learning.
#
# Indeed, we trained and predicted on the same dataset. Since our decision tree
# was fully grown, every sample in the dataset is stored in a leaf node.
# Therefore, our decision tree fully memorized the dataset given during `fit`
# and make no single error when predicting on the same data.
#
# This error computed above is called the **empirical error** or **training
# error**.
#
# We trained a predictive model to minimize the empirical error but our aim is
# to minimize the error on data that has not been seen during training.
#
# This error is also called the **generalization error** or the "true"
# **testing error**. Thus, the most basic evaluation involves:
#
# * splitting our dataset into two subsets: a training set and a testing set;
# * fitting the model on the training set;
# * estimating the empirical error on the training set;
# * estimating the generalization error on the testing set.

# %%
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

# %%
regressor.fit(X_train, y_train)

# %%
y_pred = regressor.predict(X_train)
score = mean_absolute_error(y_pred, y_train)
print(f"The empirical error of our model is {score:.2f} k$")

# %%
y_pred = regressor.predict(X_test)
score = mean_absolute_error(y_pred, y_test)
print(f"The generalization error of our model is {score:.2f} k$")

# %% [markdown]
# ## Stability of the cross-validation estimates
#
# When doing a single train-test split we don't give any indication
# regarding the robustness of the evaluation of our predictive model: in
# particular, if the test set is small, this estimate of the generalization
# error can be unstable and do not reflect the "true error rate" we would have
# observed with the same model on an unlimited amount of test data.
#
# For instance, we could have been lucky when we did our random split of our
# limited dataset and isolated some of the easiest cases to predict in the
# testing set just by chance: the estimation of the generalization error would
# be overly optimistic, in this case.
#
# **Cross-validation** allows estimating the robustness of a predictive model
# by repeating the splitting procedure. It will give several empirical and
# generalization errors and thus some **estimate of the variability of the
# model performance**.
#
# There are different cross-validation strategies, for now we are going to
# focus on one called "shuffle-split". At each iteration of this strategy we:
#
# - shuffle the order of the samples of a copy of the full data at random;
# - split the shuffled dataset into a train and a test set;
# - train a new model on the train set;
# - evaluate the generalization error on the test set.
#
# We repeat this procedure `n_splits` times. Using `n_splits=30` means that we
# will train 30 models in total and all of them will be discarded: we just
# record their performance on each variant of the test set.
#
# To evaluate the performance of our regressor, we can use `cross_validate`
# with a `ShuffleSplit` object:

# %%
import pandas as pd
from sklearn.model_selection import cross_validate
from sklearn.model_selection import ShuffleSplit

cv = ShuffleSplit(n_splits=30, test_size=0.2)

cv_results = cross_validate(
    regressor,
    X,
    y,
    cv=cv,
    scoring="neg_mean_absolute_error",
)
cv_results = pd.DataFrame(cv_results)

# %% [markdown]
# By convention, scikit-learn model evaluation tools always use a convention
# where "higher is better", this explains we used
# `scoring="neg_mean_absolute_error"` (meaning "negative mean absolute error").
#
# Let us revert the negation to get the actual error and not the negative
# score:

# %%
cv_results["test_error"] = -cv_results["test_score"]

# %% [markdown]
# Let's check the results reported by the cross-validation.

# %%
cv_results.head(10)

# %% [markdown]
# We get timing information to fit and predict at each round of
# cross-validation. Also, we get the test score, which corresponds to the
# generalization error on each of the split.

# %%
len(cv_results)

# %% [markdown]
# We get 30 entries in our resulting dataframe because we performed 30 splits.
# Therefore, we can show the generalization error distribution and thus, have
# an estimate of its variability.

# %%
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_context("talk")

sns.displot(cv_results["test_error"], kde=True, bins=10)
_ = plt.xlabel("Mean absolute error (k$)")

# %% [markdown]
# We observe that the generalization error is clustered around 45.5 k\\$ and
# ranges from 43 k\\$ to 49 k\\$.

# %%
print(
    f"The mean cross-validated generalization error is: "
    f"{cv_results['test_error'].mean():.2f} k$"
)

# %%
print(
    f"The standard deviation of the generalization error is: "
    f"{cv_results['test_error'].std():.2f} k$"
)
# %% [markdown]
# Note that the standard deviation is much smaller than the mean:
# we could summarize that our cross-validation estimate of the
# generalization error is 45.7 +/- 1.1 k\\$.
#
# If we were to train a single model on the full dataset (without
# cross-validation) and then had later access to an unlimited
# amount of test data, we would expect its true generalization
# error to fall close to that region.
#
# While this information is interesting in it-self, this should be
# contrasted to the scale of the natural variability of the target `y`
# in our dataset.
#
# Let us plot the distribution of the target variable:

# %%
sns.displot(y, kde=True, bins=20)
_ = plt.xlabel("Median House Value (k$)")

# %%
print(f"The standard deviation of the target is: {y.std():.2f} k$")

# %% [markdown]
# The target variable ranges from close to 0 k\\$ up to 500 k\\$ and, with a
# standard deviation around 115 k\\$.
#
# We notice that the mean estimate of the generalization error obtained
# by cross-validation is a bit than the natural scale of variation
# of the target variable. Furthermore the standard deviation of the cross
# validation estimate of the generalization error is even much smaller.
#
# This is a good start, but not necessarily enough to decide whether the
# generalization performance is good enough to make our prediction useful in
# practice.
#
# We recall that our model makes, on average, an error around 45 k\$. With this
# information and looking at the target distribution, such an error might be
# acceptable when predicting houses with a 500 k\\$. However, it would be an
# issue with a house with a value of 50 k\\$. Thus, this indicates that our
# metric (Mean Absolute Error) is not ideal.
#
# We might instead choose a metric relative to the target
# value to predict: the mean absolute percentage error would have been a much
# better choice.
#
# But in all cases, an error of 45 k\$ might be too large to automatically use
# our model to tag house value without expert supervision.
#
# To better understand the performance of our model and maybe find insights
# on how to improve it we will compare the generalization
# error with the empirical error. Thus, we need to compute the error on the
# training set, which is possible using the `cross_validate` function.

# %%
cv_results = cross_validate(
    regressor,
    X,
    y,
    cv=cv,
    scoring="neg_mean_absolute_error",
    return_train_score=True,
    n_jobs=2,
)
cv_results = pd.DataFrame(cv_results)

# %%
scores = pd.DataFrame()
scores[["train_error", "test_score"]] = -cv_results[
    ["train_score", "test_score"]
]
sns.histplot(scores, bins=50)
_ = plt.xlabel("Mean absolute error (k$)")

# %% [markdown]
# By plotting the distribution of the empirical and generalization errors, we
# get information about whether our model is over-fitting, under-fitting (or
# both at the same time).
#
# Here, we observe a **small empirical error** (actually zero), meaning that
# the model is **not under-fitting**: it is flexible enough to capture any
# variations present in the training set.
#
# However the **significantly larger generalization error** tells us that the
# model is **over-fitting**: the model has memorized many variations of the
# training set that could be considered "noisy" because they do not generalize
# to help us make good prediction on the test set.
#
# Some model hyper-parameters are usually the key to go from a model that
# underfits to a model that overfits, hopefully going through a region were we
# can get a good balance between the two. We can acquire knowledge by plotting
# a curve called the validation curve. This curve applies the above experiment
# and varies the value of a hyper-parameter.
#
# For the decision tree, the `max_depth` the main parameter to control the
# trade-off between under-fitting and over-fitting.

# %%
# %%time
from sklearn.model_selection import validation_curve

max_depth = [1, 5, 10, 15, 20, 25]
train_scores, test_scores = validation_curve(
    regressor,
    X,
    y,
    param_name="max_depth",
    param_range=max_depth,
    cv=cv,
    scoring="neg_mean_absolute_error",
    n_jobs=2,
)
train_errors, test_errors = -train_scores, -test_scores

# %%
_, ax = plt.subplots()

for name, errors in zip(
    ["Empirical error", "Generalization error"], [train_errors, test_errors]
):
    ax.plot(
        max_depth,
        errors.mean(axis=1),
        linestyle="-.",
        label=name,
        alpha=0.8,
    )
    ax.fill_between(
        max_depth,
        errors.mean(axis=1) - errors.std(axis=1),
        errors.mean(axis=1) + errors.std(axis=1),
        alpha=0.5,
        label=f"std. dev. {name.lower()}",
    )

ax.set_xticks(max_depth)
ax.set_xlabel("Maximum depth of decision tree")
ax.set_ylabel("Mean absolute error (k$)")
ax.set_title("Validation curve for decision tree")
_ = plt.legend(bbox_to_anchor=(1.05, 0.8), loc="upper left")

# %% [markdown]
# The validation curve can be divided into three areas:
#
# - For `max_depth < 10`, the decision tree underfits. The empirical error and
#   therefore also the generalization error are both high. The model is too
#   constrained and cannot capture much of the variability of the target
#   variable.
#
#
# - The region around `max_depth = 10` corresponds to the parameter for which
#   the decision tree generalizes the best. It is flexible enough to capture a
#   fraction of the variability of the target that generalizes, while not
#   memorizing all of the noise in the target.
#
#
# - For `max_depth > 10`, the decision tree overfits. The empirical error
#   becomes very small, while the generalization error increases. In this
#   region, the models captures too much of the noisy part of the variations of
#   the target and this harms its ability to generalize well to test data.
#
#
# Note that for `max_depth = 10`, the model overfits a bit as there is a gap
# between the empirical error and the generalization error. It can also
# potentially underfit also a bit at the same time, because the empirical error
# is still far from zero (more than 30 k\\$), meaning that the model might
# still be too constrained to model interesting parts of the data. However the
# generalization error is minimal, and this is what really matters. This is the
# best compromise we could reach by just tuning this parameter.
#
# We were lucky that the variance of the errors was small compared to their
# respective values, and therefore the conclusions above are quite clear. This
# is not necessarily always the case.
#
# We will now focus on one factor that can affect this variance, namely, the
# size of the dataset:

# %%
y.size

# %% [markdown]
# Let's do an experiment and reduce the number of samples and repeat the
# previous experiment.


# %%
def make_cv_analysis(regressor, X, y):
    cv = ShuffleSplit(n_splits=10, test_size=0.2)
    cv_results = pd.DataFrame(
        cross_validate(
            regressor,
            X,
            y,
            cv=cv,
            scoring="neg_mean_absolute_error",
            return_train_score=True,
        )
    )
    return (cv_results["test_score"] * -1).values


# %%
import numpy as np

sample_sizes = [100, 500, 1000, 5000, 10000, 15000, y.size]

scores_sample_sizes = {"# samples": [], "test score": []}
rng = np.random.RandomState(0)
for n_samples in sample_sizes:
    sample_idx = rng.choice(np.arange(y.size), size=n_samples, replace=False)
    X_sampled, y_sampled = X.iloc[sample_idx], y[sample_idx]
    score = make_cv_analysis(regressor, X_sampled, y_sampled)
    scores_sample_sizes["# samples"].append(n_samples)
    scores_sample_sizes["test score"].append(score)

scores_sample_sizes = pd.DataFrame(
    np.array(scores_sample_sizes["test score"]).T,
    columns=scores_sample_sizes["# samples"],
)

# %%
sns.displot(scores_sample_sizes, kind="kde")
plt.xlabel("Mean absolute error (k$)")
_ = plt.title(
    "Generalization errors distribution \nby varying the sample size"
)

# %% [markdown]
# For the different sample sizes, we plotted the distribution of the
# generalization error. We observe that smaller is the sample size; larger is
# the variance of the generalization errors. Thus, having a small number of
# samples might put us in a situation where it is impossible to get a reliable
# evaluation.
#
# Here, we plotted the different curve to highlight the issue of small sample
# size. However, this experiment is also used to draw the so-called **learning
# curve**. This curve gives some additional indication regarding the benefit of
# adding new training samples to improve a model's performance.

# %%
from sklearn.model_selection import learning_curve

results = learning_curve(
    regressor,
    X,
    y,
    train_sizes=sample_sizes[:-1],
    cv=cv,
    scoring="neg_mean_absolute_error",
    n_jobs=2,
)
train_size, train_scores, test_scores = results[:3]
train_errors, test_errors = -train_scores, -test_scores

# %%
_, ax = plt.subplots()

for name, errors in zip(
    ["Empirical error", "Generalization error"], [train_errors, test_errors]
):
    ax.plot(
        max_depth,
        errors.mean(axis=1),
        linestyle="-.",
        label=name,
        alpha=0.8,
    )
    ax.fill_between(
        max_depth,
        errors.mean(axis=1) - errors.std(axis=1),
        errors.mean(axis=1) + errors.std(axis=1),
        alpha=0.5,
        label=f"std. dev. {name.lower()}",
    )

ax.set_xticks(train_size)
ax.set_xscale("log")
ax.set_xlabel("Number of samples in the training set")
ax.set_ylabel("Mean absolute error (k$)")
ax.set_title("Learning curve for decision tree")
_ = plt.legend(bbox_to_anchor=(1.05, 0.8), loc="upper left")

# %% [markdown]
# We see that the more samples we add to the training set on this learning
# curve, the lower the error becomes. With this curve, we are searching for the
# plateau for which there is no benefit to adding samples anymore or assessing
# the potential gain of adding more samples into the training set.
#
# For this dataset we notice that our decision tree model would really benefit
# from additional datapoints to reduce the amount of over-fitting and hopefully
# reduce the generalization error even further.
