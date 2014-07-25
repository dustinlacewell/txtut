import sys

from twisted.internet import defer, task, reactor, protocol

class Pipe(defer.Deferred, protocol.ProcessProtocol):
    def __init__(self, input=None):
        defer.Deferred.__init__(self)
        self.input = input
        self.output = ""

    def connectionMade(self):
        if self.input:
            self.transport.write(self.input)
        self.transport.closeStdin()

    def outReceived(self, data):
        self.output += data

    def processEnded(self, reason):
        self.callback(self.output)

def make_pipe(cmd, *args, **kwargs):
    '''create a deferred that fires with the output of the process'''
    pipe = Pipe(kwargs.get('stdin'))
    args = [cmd] + list(args)
    reactor.spawnProcess(pipe, cmd, args)
    return pipe

def exceptional_pipe(*args, **kwargs):
    raise Exception('Whoopsie')

def failing_pipe(*args, **kwargs):
    d = defer.Deferred()

    def fail():
        d.errback(Exception('Hello?'))

    reactor.callLater(2, fail)

    return d

def get_data(n):
    '''emulate network retreival of some data'''
    return make_pipe('head', '-c', str(n), '/dev/random')

def count_words(d):
    '''emulate sending data to remote service for processing'''
    return failing_pipe('wc', '-w', stdin=d)

def save_result(c, filename):
    print "Writing result to file:", filename
    return make_pipe('tee', filename, stdin=c.strip())

@defer.inlineCallbacks
def start():
    data = yield get_data(1024)
    words = yield count_words(data)
    yield save_result(words, '/tmp/result.txt')
    reactor.stop()

def failsafe(failure):
    print "Failure!"
    print failure
    reactor.stop()

d = start()
d.addErrback(failsafe)

reactor.run()
