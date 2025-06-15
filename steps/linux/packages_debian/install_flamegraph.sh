#!/bin/sh

wget https://github.com/brendangregg/FlameGraph/archive/refs/tags/v1.0.zip
unzip v1.0.zip
sudo cp FlameGraph-1.0/flamegraph.pl /usr/local/bin/flamegraph.pl
sudo chown root:root /usr/local/bin/flamegraph.pl
sudo chmod 755 /usr/local/bin/flamegraph.pl
