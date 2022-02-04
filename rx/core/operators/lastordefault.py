from typing import Any, Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, abc, typing
from rx.internal.exceptions import SequenceContainsNoElementsError

_T = TypeVar("_T")


def last_or_default_async(
    source: Observable[_T], has_default: bool = False, default_value: Any = None
) -> Observable[_T]:
    def subscribe(observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase] = None):
        value = [default_value]
        seen_value = [False]

        def on_next(x: _T) -> None:
            value[0] = x
            seen_value[0] = True

        def on_completed():
            if not seen_value[0] and not has_default:
                observer.on_error(SequenceContainsNoElementsError())
            else:
                observer.on_next(value[0])
                observer.on_completed()

        return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)

    return Observable(subscribe)


def last_or_default(
    predicate: Optional[typing.Predicate[_T]] = None, default_value: Any = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    def last_or_default(source: Observable[_T]) -> Observable[_T]:
        """Return last or default element.

        Examples:
            >>> res = _last_or_default(source)

        Args:
            source: Observable sequence to get the last item from.

        Returns:
            Observable sequence containing the last element in the
            observable sequence.
        """

        if predicate:
            return source.pipe(
                ops.filter(predicate),
                ops.last_or_default(None, default_value),
            )

        return last_or_default_async(source, True, default_value)

    return last_or_default

__all__ = [ "last_or_default", "last_or_default_async"]