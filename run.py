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

def get_data(n):
    '''emulate network retreival of some data'''
    return make_pipe('head', '-c', str(n), '/dev/random')

def result(output):
    '''take some data and print out how many words there are'''
    print len(output.split())

# get some data
(get_data(1024)
    # then process the data
    .addCallback(result)
    # then stop the reactor
    .addCallback(lambda _: reactor.stop()))

reactor.run()