class ClusteringModel:
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans

    INDEX_NAME = "char"
    WIDTH_NAME = "width"
    WEIGHT_NAME = "weight"
    CLUSTER_NAME = "cluster"
    CLUSTER_WIDTH_NAME = "cluster_width"

    predictor = None
    extra_symbol_width = None

    def __init__(self,
                 calc_cluster_width=None,
                 allow_extra_symbols=True,
                 index_name=INDEX_NAME,
                 width_name=WIDTH_NAME,
                 weight_name=WEIGHT_NAME,
                 cluster_name=CLUSTER_NAME,
                 cluster_width_name=CLUSTER_WIDTH_NAME,
                 **kmean_parameters):
        self.calc_cluster_width = calc_cluster_width
        self.allow_extra_symbols = allow_extra_symbols
        self.kmean_parameters = kmean_parameters
        self.index_name = index_name
        self.width_name = width_name
        self.weight_name = weight_name
        self.cluster_name = cluster_name
        self.cluster_width_name = cluster_width_name

    def fit(self, char_data, *, admixture=None):
        if admixture is None:
            self.predictor = self._prepare_predictor(char_data, self.kmean_parameters)
        else:
            self.predictor = pd.concat([
                self._prepare_predictor(
                    char_data[char_data[admixture] == admixture_key],
                    {**self.kmean_parameters, **{"n_clusters": admixture_n_clusters}},
                    "{0}-".format(admixture_id)
                )
                for admixture_id, (admixture_key, admixture_n_clusters) \
                    in enumerate(self._calc_admixture_clusters(char_data[admixture].value_counts()).items())
            ])
        self.extra_symbol_width = (self.calc_cluster_width or self._calc_cluster_width)(self.predictor)
        return self

    def predict(self, text, name=None):
        if isinstance(text, str):
            return round(self.np.sum([self._predict_char_width(c) for c in text]))
        elif isinstance(text, self.pd.core.series.Series):
            return self._predict_for_series(text, name if (isinstance(name, str)) else None)
        elif isinstance(text, self.pd.core.frame.DataFrame):
            return self.pd.concat([
                self._predict_for_series(text[column], name[column] if (isinstance(name, dict)) else None)
                for column in text.columns
            ], axis="columns")
        else:
            raise Exception("Bad type of input: {0}".format(type(text)))

    def _calc_admixture_clusters(self, admixture_counts):
        n_admixtures = admixture_counts.shape[0]
        n_clusters = self.kmean_parameters.get("n_clusters", n_admixtures)
        if n_clusters < n_admixtures:
            raise Exception("Too few clusters: {0} < {1}".format(n_clusters, n_admixtures))
        result = {}
        for admixture, ratio in (admixture_counts.sort_values() / admixture_counts.sum()).iteritems():
            result[admixture] = max(1, round(n_clusters * ratio))
        return result

    def _prepare_predictor(self, char_data, kmean_parameters, admixture_prefix=""):
        predictor_df = char_data[[self.width_name, self.weight_name]]
        predictor_df.index.name = self.index_name
        # Set clusters
        predictor_df[self.cluster_name] = self.KMeans(**kmean_parameters).fit(predictor_df[[self.width_name]]).labels_
        # Set cluster widths
        cluster_widths = predictor_df.groupby(self.cluster_name).apply(self.calc_cluster_width or self._calc_cluster_width)
        predictor_df[self.cluster_width_name] = predictor_df[self.cluster_name].replace(cluster_widths)
        # Sort clusters
        predictor_df.sort_values(by=self.cluster_width_name, inplace=True)
        predictor_df.cluster.replace(
            {cluster_id: "{0}{1}".format(admixture_prefix, i) \
             for i, cluster_id in enumerate(predictor_df[self.cluster_name].unique())},
            inplace=True
        )
        return predictor_df

    def _calc_cluster_width(self, r):
        return (r.width * r.weight).sum() / r.weight.sum()

    def _predict_char_width(self, c):
        try:
            return self.predictor.loc[c].cluster_width
        except KeyError as e:
            if self.allow_extra_symbols:
                return self.extra_symbol_width
            else:
                raise e

    def _predict_for_series(self, text_s, name=None):
        def split_string(s):
            return self.pd.Series([s[i:i+1] for i in range(len(s))])
        df = text_s.apply(split_string)
        splitted_df = df.replace(self.predictor.cluster_width).fillna(0)
        cols = splitted_df.columns
        result = splitted_df[cols].apply(self.pd.to_numeric, errors='coerce', axis=1)\
                                  .fillna(self.extra_symbol_width).sum(axis=1).round().astype(int)
        result.name = name or "predict_{0}".format(text_s.name)
        return result