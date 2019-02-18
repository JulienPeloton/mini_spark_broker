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
from pyspark.sql.streaming import StreamingQuery

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import time

def recentrecentProgress(query: StreamingQuery, colnames: list, waitfor: int=0):
    """ Register recent query progresses in a Pandas DataFrame.

    It turns out that Structured Streaming cannot be monitored as Streaming
    in the Spark UI (which is a shame...), hence this simple routine to be
    able to quickly plot progress.

    Parameters
    ----------
    query: StreamingQuery
        StreamingQuery query.
    colnames: list of str
        Fields of the query.recentProgress to be registered
    waitfor: int, optional
        If specified, wait for `waitfor` seconds. Default is 0.

    Returns
    ----------
    data: pd.DataFrame
        Pandas DataFrame whose columns are colnames, and index
        is the timestamp.
    """
    time.sleep(waitfor)

    # Force to register timestamp
    if "timestamp" not in colnames:
        colnames.append(timestamp)

    # Register fields in a dic
    dicval = {i: [] for i in colnames}
    timestamp = []
    for c in query.recentProgress:
        if len(c) == 0:
            continue
        try:
            for colname in colnames:
                dicval[colname].append(c[colname])
        except (TypeError, KeyError):
            # This can happen if the stream has not begun
            # or is stuck.
            continue

    # Build DataFrame from dic
    data = pd.DataFrame(dicval)

    # Set timestamp as index
    data.set_index('timestamp',inplace=True)

    # Format it as datetime (useful for plot)
    data.index = pd.to_datetime(data.index)

    return data

def show_stream_process(ax, query, colnames):
    """
    Will return data only if the stream is live!
    """
    dfp = recentrecentProgress(query, colnames)
    if dfp.empty:
        return True
    plt.cla()
    dfp.plot(ax=ax)
    ax.set_ylabel("Rows Per Second")
    plt.grid()
    # plt.show(block=False)
    plt.draw()
