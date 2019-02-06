# Copyright 2018 Julien Peloton
# Author: Julien Peloton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def extract_history_ztf(alert, key):
    """Extract data field from alert candidate and previous linked alerts.

    Parameters
    ----------
    candidate: dict
        Correspond to the key "candidate" in the alert dictionary.
    previous: list of dicts
        Correspond to the key "prv_candidates" in the alert dictionary.
    key: str
        Dictionary key for which values have to be extracted

    Returns
    ----------
    out: list
        List containing values corresponding to the key. First element is
        from the candidate, and other elements from the previous alerts.
    """
    data = [i[key] for i in alert["prv_candidates"]]
    data.insert(0, alert["candidate"][key])

    return data

def ret(d, key):
    """ Unwrap nested dictionaries in a recursive way.

    Parameters
    ----------
    d: dict
        Python dictionary
    key: str or Any
        Key or chain of keys. See example below to
        access nested levels.

    Returns
    ----------
    out: Any
        Value from the key or value from the
        last key from the chains.


    Examples
    ----------
    >>> a = {"toto": {"titi":1}, "tutu":2}
    >>> ret(a, "tutu")
    2

    >>> ret(a, "toto")
    {"titi":1}

    >>> ret(a, "toto:titi")
    1
    """
    if ":" in key:
        # Split at first ":"
        level = key.split(":", maxsplit=1)
        if isinstance(d[level[0]], dict):
            return ret(d[level[0]], level[1])
        else:
            raise AssertionError("""
            Nested level must be dictionaries!
            d[{}] is not a dict!
            """.format(level[0]))
    return d[key]

def make_dataframe_from_alerts(rdd, colnames):
    """ Make a Dataframe from a RDD of alerts and columns names.

    Parameters
    ----------
    rdd: Apache Spark RDD of dictionaries
        RDD whose elements are dictionaries (decoded alerts)
    colnames: list of str
        List containing the keys to include. For nested levels, just chain
        it using double dot: firstdic:seconddic:key
    """
    return rdd.map(lambda x: tuple(ret(x, k) for k in colnames)).toDF(colnames)
