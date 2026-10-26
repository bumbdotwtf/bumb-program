#!/bin/sh
compiler=$1
shift
case " $* " in
  *" --crate-name pump_recovered "*)
    exec "$compiler" "$@" --remap-path-prefix=src=programs/pump/src
    ;;
  *)
    exec "$compiler" "$@"
    ;;
esac
