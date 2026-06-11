def executar_benchmark(*args, **kwargs):
    from .benchmark import executar_benchmark as _run
    return _run(*args, **kwargs)

__all__ = ["executar_benchmark"]
