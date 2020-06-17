# %% [markdown]
# # Evaluate of your predictive model

# %% [markdown]
# ## Introduction
# Machine-learning models rely on optimizing an objective function, by seeking
# its minimum or maximum. It is important to understand that this objective
# function is usually decoupled from the evaluation metric that we want to
# optimize in practice. The objective function serves as a proxy to the
# evaluation metric.
#
# While other notebooks will give insights regarding algorithms and their
# associated objective functions, in this notebook we will focus on the
# metrics used to evaluate the performance of a predictive model.
#
# Selecting an evaluation metric will mainly depend on the model chosen to
# solve our datascience problem.

# %% [markdown]
# ## Classification
# We can recall that in a classification setting, the target `y` is categorical
# rather than continuous. We will use the blood transfusion dataset that will
# be fetched from OpenML.

# %%
import pandas as pd
from sklearn.datasets import fetch_openml

X, y = fetch_openml(
    name="blood-transfusion-service-center",
    as_frame=True, return_X_y=True,
)
# Make columns and classes more human-readable
X.columns = ["Recency", "Frequency", "Monetary", "Time"]
y = y.apply(
    lambda x: "donated" if x == "2" else "not donated"
).astype("category")
y.cat.categories

# %% [markdown]
# We can see that the target `y` contains 2 categories corresponding to whether
# or not a subject gave blood or not. We will use a logistic regression
# classifier to predict this outcome.
#
# First, we split the data into a training and a testing set.

# %%
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, shuffle=True, random_state=0, test_size=0.5
)

# %% [markdown]
# Once our data are split, we can learn a logistic regression classifier solely
# on the training data, keeping the testing data for the evaluation of the
# model.

# %%
from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression()
classifier.fit(X_train, y_train)

# %% Now, that our classifier is trained, we can provide a some [markdown]
# information about a subject and the classifier can predict whether or not the
# subject will donate blood.
#
# Let's create a synthetic sample corresponding to the following potential
# donor: he/she donated blood 6 month ago and gave twice blood in the past for
# a total of 1000 c.c. He/she gave blood for the first time 20 months ago.

# %%
new_donor = [[6, 2, 1000, 20]]
classifier.predict(new_donor)

# %% [markdown]
# With these information, our classifier predicted that this synthetic subject
# is more likely to not donate blood. However, we have no possibility to ensure
# if the prediction is correct or not. That's why, we can now use the testing
# set for this purpose. First, we can predict whether or not a subject will
# give blood with the help of the trained classifier.

# %%
y_pred = classifier.predict(X_test)
y_pred

# %% [markdown]
# ### Accuracy as a baseline
# Now that we have these predictions, we could compare them with the true
# predictions (sometimes called ground-truth) which we did not use up to now.

# %%
y_test == y_pred

# %% [markdown]
# In the comparison above, a `True` value means that the value predicted by our
# classifier is identical to the real `prediction` while a `False` means that
# our classifier made a mistake. One way to get an overall statistic telling us
# how good the performance of our classifier are is the computer the number of
# time our classifier was right and divide it by the number of samples in our
# set.

# %%
import numpy as np

np.mean(y_test == y_pred)

# %% [markdown]
# This measure is also known as the accuracy. Here, our classifier is 97%
# accurate at classifying iris flowers. `scikit-learn` provides a function to
# compute this metric in the module `sklearn.metrics`.

# %%
from sklearn.metrics import accuracy_score

accuracy_score(y_test, y_pred)

# %% [markdown]
# Our classifier give the good answer in 77% of the case.
#
# Scikit-learn also have a build-in method named `score` which compute by
# default the accuracy score.

# %%
classifier.score(X_test, y_test)

# %% [markdown]
# ### Confusion matrix and derived metrics
# The comparison that we did above and the accuracy that we deducted did not
# take into account which type of error our classifier was doing. The accuracy
# is an aggregate of the error. However, we might be interested in a lower
# granularity level to know separately the error for the two following case:
# - we predicted that a person will give blood but she/he is not;
# - we predicted that a person will not give blood but she/he is.

# %%
from sklearn.metrics import plot_confusion_matrix

plot_confusion_matrix(classifier, X_test, y_test)

# %% The in-diagonal numbers are related to predictions that agree [markdown]
# with the true labels while off-diagonal numbers are related to
# misclassification. Besides, we now know the type of true or erroneous
# predictions the classifier did:
#
# * the top left corner is called true positive (TP) and correspond to a person
#   who gave blood and was predicted as such by the classifier;
# * the bottom right corner is called the true negative (TN) and correspond to
#   a person who did not gave blood and was predicted as such by the
#   classifier;
# * the top right corner is called false negative (FN) and correspond to a
#   person who gave blood but was predicted as not giving blood;
# * the bottom left corner is called false positive (FP) and correspond to a
#   person who did not give blood but was predicted as giving blood.
#
# Once that we have split these information, we can compute statistic for a
# highlighting the performance of our classifier in a particular setting. For
# instance, one could be interested in the fraction of persons who really gave
# blood when the classifier predicted so or the fraction of people predicted as
# giving blood among the total population that actually did so.
#
# The former statistic is known as the precision defined as TP / (TP + FP)
# while the latter statistic is known as the recall defined as TP / (TP + FN)
# We could, similarly than with the accuracy, manually compute these values.
# But scikit-learn provides functions to compute these statistics.

# %%
from sklearn.metrics import precision_score, recall_score

print(
    f"Precision score: {precision_score(y_test, y_pred, pos_label='donated')}"
    f"\nRecall score: {recall_score(y_test, y_pred, pos_label='donated')}"
)

# %% [markdown]
# These results are in line with what we could see in the confusion matrix.
# In the left column, more than half of the predictions were corrected leading
# to a precision above 0.5. However, our classifier mislabeled a lot of persons
# who gave blood as "not donated" leading to a very low recall of around 0.1.
#
# The precision and recall can be combined in a single score called the F1
# score

# %%
from sklearn.metrics import f1_score

f1_score(y_test, y_pred, pos_label='donated')

# %% [markdown]
# ### The issue of class imbalance
# At this stage, we could ask ourself a reasonable question. While the accuracy
# did not look bad (i.e. 77%), the F1 score is relatively low (i.e. 21%).
#
# As we mentioned, precision and recall only focus on the positive label while
# the accuracy is taking into account both aspects into account. In addition,
# we important thing that we omit up to know is to look at the ratio class
# occurrence. We could check this ratio in the training set.

# %%
from collections import Counter

class_counts = pd.Series(Counter(y_train))
class_counts /= class_counts.sum()
class_counts

# %% [markdown]
# So we can observed that the positive class `'donated'` is only 24% of the
# total number of instances. The good accuracy of our classifier is then linked
# to its capability of predicting correctly the negative class `'not donated'`
# which could be relevant or not depending of the application. We can
# illustrate the issue using a dummy classifier as a baseline.

# %%
from sklearn.dummy import DummyClassifier

dummy_classifier = DummyClassifier(
    strategy="constant", constant="not donated"
)
dummy_classifier.fit(X_train, y_train).score(X_test, y_test)

# %% [markdown]
# This dummy classifier will always predict the negative class `'not donated'`.
# We obtain an accuracy score of 76%. Therefore, it means that this classifier,
# without learning anything from the data `X` is capable of predicting as
# accurately than our logistic regression. 76% represents the baseline that
# any classifier should overperform to not be a random classifier.
#
# The problem illustrated above is also known as the class imbalance problem
# where the accuracy should not be used. In this case, one should either use
# the precision, recall, or F1 score as presented above or the balanced
# accuracy score instead of the accuracy.

# %%
from sklearn.metrics import balanced_accuracy_score

balanced_accuracy_score(y_test, y_pred)
# %% [markdown]
# The balanced accuracy is equivalent to the accuracy in the context of
# balanced classes. It is defined as the average recall obtained on each class.
#
# ### Evaluation with different probability threshold
#
# All statistics that we presented up to now rely on `classifier.predict` which
# provide the most likely label. However, we don't use the probability
# associated with this prediction or in other words how sure are the classifier
# confident about this prediction. By default, the prediction of a classifier
# correspons to a thresholding at a 0.5 probability, in a binary classification
# problem. We can quickly check this relationship with the classifier that
# we trained.

# %%
y_proba = pd.DataFrame(
    classifier.predict_proba(X_test),
    columns=classifier.classes_
)
y_proba[:5]

# %%
y_pred = classifier.predict(X_test)
y_pred[:5]

# %%
# Since probabilities sum to 1 we can get the class with the highest
# probability without using the threshold 0.5
equivalence_pred_proba = (
    y_proba.idxmax(axis=1).to_numpy() == y_pred
)
np.all(equivalence_pred_proba)

# %% [markdown]
# The default decision threshold might not be the best threshold leading to
# optimal performance of our classifier. In this case, one can vary the
# decision threshold and therefore the underlying prediction and compute the
# same statistic than presented earlier. Usually, two metrics are computed
# and reported as a curve. Each metric is belonging to a graph axis and a point
# on the graph corresponds to a specific decision threshold. Let's start by
# computing the precision-recall curve.

# %%
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score

y_pred = classifier.predict_proba(X_test)
pos_label = "donated"
precision, recall, threshold = precision_recall_curve(
    y_test, y_pred[:, 0], pos_label=pos_label,
)
average_precision = average_precision_score(
    y_test, y_pred[:, 0], pos_label=pos_label,
)
plt.plot(
    recall, precision,
    color="tab:orange", linewidth=3,
    marker=".", markerfacecolor="tab:blue", markeredgecolor="tab:blue",
    label=f"Average Precision: {average_precision:.2f}",
)
plt.xlabel(f"Recall\n (Positive label: {pos_label})")
plt.ylabel(f"Precision\n (Positive label: {pos_label})")
plt.legend()

# # FIXME: to be used when solved in scikit-learn
# from sklearn.metrics import plot_precision_recall_curve

# disp = plot_precision_recall_curve(
#     classifier, X_test, y_test, pos_label='donated',
# )

# %% [markdown]
# On this curve, each blue dot correspond to a certain level of probability
# which we used as a decision threshold. We can see that by varying this
# decision threshold, we get different compromise precision vs. recall.
#
# A perfect classifier is expected to have a precision at 1 even when varying
# the recall. A metric characterizing the curve is linked to the area under the
# curve (AUC), named averaged precision. With a ideal classifier, the
# average precision will be 1.
#
# While the precision and recall metric focuses on the positive class, one
# might be interested into the compromise between performance to discriminate
# positive and negative classes. The statistics used in this case are the
# sensitivity and specificity. The sensitivity is just another denomination for
# recall. However, the specificity measures the proportion of well classified
# samples from the negative class defined as TN / (TN + FP). Similarly to the
# precision-recall curve, sensitivity and specificity are reported with a curve
# called the receiver operating characteristic (ROC) curve. We will show such
# curve:

# %%
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score

fpr, tpr, threshold = roc_curve(y_test, y_pred[:, 0], pos_label=pos_label)
# FIXME: roc_auc_score has a bug and we need to give the inverse probability
# vector. Should be changed when the following is merged and released:
# https://github.com/scikit-learn/scikit-learn/pull/17594
roc_auc = roc_auc_score(y_test, y_pred[:, 1])
plt.plot(
    fpr, tpr,
    color="tab:orange", linewidth=3,
    marker=".", markerfacecolor="tab:blue", markeredgecolor="tab:blue",
    label=f"ROC-AUC: {roc_auc:.2f}"
)
plt.plot([0, 1], [0, 1], "--", color="tab:green", label="Chance")
plt.xlabel(f"1 - Specificity\n (Positive label: {pos_label})")
plt.ylabel(f"Sensitivity\n (Positive label: {pos_label})")
plt.legend()

# # FIXME: to be used when solved in scikit-learn
# from sklearn.metrics import plot_roc_curve

# plot_roc_curve(classifier, X_test, y_test, pos_label='donated')

# %% [markdown]
# This curve is built with the same principle than with the precision-recall
# curve: we vary the probability threshold to compute "hard" prediction and
# compute the metrics. As with the precision-recall curve as well, we can
# compute the area under the ROC (ROC-AUC) to characterize the performance of
# our classifier. However, this is important to observer that the lower bound
# of the ROC-AUC is 0.5. Indeed, we represented the performance of a dummy
# classifier (i.e. green dashed line) to show that the worse performance
# obtained will always be above this line.
#
# ### Link between confusion matrix, precision-recall curve and ROC curve
#
# TODO: ipywidgets to play with interactive curve

# %%
def plot_pr_curve(classifier, X_test, y_test, pos_label, probability_threshold, ax):
    y_pred = classifier.predict_proba(X_test)
    precision, recall, threshold = precision_recall_curve(
        y_test, y_pred[:, 0], pos_label=pos_label,
    )
    average_precision = average_precision_score(
        y_test, y_pred[:, 0], pos_label=pos_label,
    )
    ax.plot(
        recall, precision,
        color="tab:orange", linewidth=3,
        label=f"Average Precision: {average_precision:.2f}",
    )
    threshold_idx = np.searchsorted(
        threshold, probability_threshold,
    )
    ax.plot(
        recall[threshold_idx], precision[threshold_idx],
        color="tab:blue", marker=".", markersize=10,
    )
    ax.plot(
        [recall[threshold_idx], recall[threshold_idx]],
        [0, precision[threshold_idx]],
        '--', color="tab:blue",
    )
    ax.plot(
        [0, recall[threshold_idx]],
        [precision[threshold_idx], precision[threshold_idx]],
        '--', color="tab:blue",
    )
    ax.set_xlabel(f"Recall")
    ax.set_ylabel(f"Precision")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.legend()
    return ax


# %%
def plot_roc_curve(classifier, X_test, y_test, pos_label, probability_threshold, ax):
    y_pred = classifier.predict_proba(X_test)
    fpr, tpr, threshold = roc_curve(y_test, y_pred[:, 0], pos_label=pos_label)
    roc_auc = roc_auc_score(y_test, y_pred[:, 1])
    ax.plot(
        fpr, tpr,
        color="tab:orange", linewidth=3,
        label=f"ROC-AUC: {roc_auc:.2f}"
    )
    ax.plot([0, 1], [0, 1], "--", color="tab:green", label="Chance")
    threshold_idx = np.searchsorted(
        threshold[::-1], probability_threshold,
    )
    threshold_idx = len(threshold) - threshold_idx - 1
    ax.plot(
        fpr[threshold_idx], tpr[threshold_idx],
        color="tab:blue", marker=".", markersize=10,
    )
    ax.plot(
        [fpr[threshold_idx], fpr[threshold_idx]],
        [0, tpr[threshold_idx]],
        '--', color="tab:blue",
    )
    ax.plot(
        [0, fpr[threshold_idx]],
        [tpr[threshold_idx], tpr[threshold_idx]],
        '--', color="tab:blue",
    )
    ax.set_xlabel(f"1 - Specificity")
    ax.set_ylabel(f"Sensitivity")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.legend()
    return ax


# %%
def plot_pr_roc(threshold):
    # FIXME: we could optimize the plotting by only updating the the
    fig, axs = plt.subplots(ncols=2, figsize=(14, 6))
    plot_pr_curve(
        classifier, X_test, y_test, pos_label="donated",
        probability_threshold=threshold, ax=axs[0],
    )
    plot_roc_curve(
        classifier, X_test, y_test, pos_label="donated",
        probability_threshold=threshold, ax=axs[1]
    )
    fig.suptitle("Overall performance with positive class 'donated'")


# %%
from ipywidgets import interactive, FloatSlider

def plot_pr_roc_interactive():
    slider = FloatSlider(min=0, max=1, step=0.01, value=0.5)
    return interactive(plot_pr_roc, threshold=slider)


# %%
plot_pr_roc_interactive()

# %% [markdown]
# ## Regression

# %% [markdown]
# ## Clustering
