def prune_features(
    column_names, cols_to_prune, target_featureset
):
    """Prunes specified columns from input list while preserving order,

    extends target_featureset, and displays the result.
    """

    prune_set = set(cols_to_prune)
    cols_to_keep = [col for col in column_names if col not in prune_set]

    # Extend with new features
    target_featureset.extend(cols_to_keep)

    # In-place order-preserving deduplication
    target_featureset[:] = list(dict.fromkeys(target_featureset))

    print(target_featureset)
    return target_featureset