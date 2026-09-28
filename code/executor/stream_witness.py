"""Fail-closed construction of a distinct-native-stream rejection witness."""


def stream_pair(admitted, candidate):
    first, second = int(admitted.cuda_stream), int(candidate.cuda_stream)
    if admitted.device != candidate.device:
        raise AssertionError('Stream witness must use the admitted device')
    if first == second:
        raise AssertionError('Stream witness aliases the admitted native handle')
    return dict(admitted_handle=first, candidate_handle=second,
                admitted_device=str(admitted.device), candidate_device=str(candidate.device))


def reject_stream_substitution(execution, admitted, candidate, rejected_type):
    witness = stream_pair(admitted, candidate)
    if execution.stream.cuda_stream != admitted.cuda_stream:
        raise AssertionError('Stream witness does not match the bound execution')
    before = (execution.stage, len(execution.events), execution.failed, execution.lease.aborted)
    if before != (1, 1, False, False):
        raise AssertionError('Stream rejection witness requires a healthy submitted prefix')
    try:
        execution.submit(1, candidate)
    except rejected_type as error:
        if str(error) != 'only one CUDA stream is supported':
            raise AssertionError('Stream witness rejected for a different reason') from error
        reason = str(error)
    else:
        raise AssertionError('Distinct native stream was accepted')
    after = (execution.stage, len(execution.events), execution.failed, execution.lease.aborted)
    if before != after:
        raise AssertionError('Rejected stream changed execution state')
    return dict(witness, reason=reason, before=list(before), after=list(after), rejected=True)
